"""
Statistics Manager - Calculates and caches statistics
Parses config and activity logs to generate insights
Includes duration tracking and chart data generation
"""

import json
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import Counter, defaultdict


class StatisticsManager:
    """Manages statistics calculation and caching"""
    
    def __init__(self, config_folder: str):
        self.config_folder = config_folder
        self.config_file = os.path.join(config_folder, 'apps_config.json')
        self.activity_log_file = os.path.join(config_folder, 'activity.log')
        self.stats_cache_file = os.path.join(config_folder, 'statistics.json')
        self.metadata_file = os.path.join(config_folder, 'metadata.json')
        self.cache_duration = 60  # seconds - recalculate if older than this
        
        # Initialize session metadata on first creation (once per app session)
        self._init_session_metadata()
        
    def _init_session_metadata(self):
        """Initialize session metadata (called once per app startup)"""
        try:
            # Create fresh metadata file with current startup time
            startup_data = {'first_startup': datetime.now().isoformat()}
            with open(self.metadata_file, 'w') as f:
                json.dump(startup_data, f, indent=2)
        except:
            pass
    
    def get_session_uptime(self) -> Dict:
        """Get FadCrypt session uptime (current app instance only)"""
        # Load the startup time from metadata (created fresh on app startup)
        startup_time = datetime.now()
        
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                    startup_time = datetime.fromisoformat(metadata.get('first_startup', datetime.now().isoformat()))
        except:
            pass
        
        # Calculate uptime
        uptime = datetime.now() - startup_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        total_hours = uptime.total_seconds() / 3600
        total_minutes = uptime.total_seconds() / 60
        
        return {
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_minutes': int(total_minutes),
            'uptime_hours': round(total_hours, 2),
            'uptime_formatted': f"{days}d {hours}h {minutes}m {seconds}s",
            'first_startup': startup_time.isoformat(),
            'current_time': datetime.now().isoformat()
        }
    
    def _get_config(self) -> Dict:
        """Load unified config"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {'applications': [], 'locked_files_and_folders': []}
        return {'applications': [], 'locked_files_and_folders': []}
    
    def _get_activity_events(self) -> List[Dict]:
        """Load all activity events"""
        if not os.path.exists(self.activity_log_file):
            return []
        
        events = []
        try:
            with open(self.activity_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        except:
            pass
        return events
    
    def calculate_stats(self) -> Dict:
        """Calculate all statistics"""
        config = self._get_config()
        events = self._get_activity_events()
        
        apps = config.get('applications', [])
        locked_items = config.get('locked_files_and_folders', [])
        
        # Basic counts
        total_apps = len(apps)
        total_locked_items = len(locked_items)
        total_items = total_apps + total_locked_items
        
        # Calculate lock/unlock counts
        total_locks = sum(app.get('unlock_count', 0) for app in apps)
        total_locks += sum(item.get('unlock_count', 0) for item in locked_items)
        
        # Most locked items - handle both structures
        most_locked = sorted(
            [(app.get('name', 'Unknown'), app.get('unlock_count', 0)) for app in apps] +
            [(item.get('path', 'Unknown'), item.get('unlock_count', 0)) for item in locked_items],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Event statistics
        lock_events = len([e for e in events if 'lock' in e.get('event_type', '')])
        unlock_events = len([e for e in events if 'unlock' in e.get('event_type', '')])
        failed_attempts = len([e for e in events if e.get('event_type') == 'failed_unlock'])
        
        # Peak lock hour
        lock_hours = [datetime.fromisoformat(e['timestamp']).hour 
                     for e in events if 'lock' in e.get('event_type', '')]
        peak_hour = max(set(lock_hours), key=lock_hours.count) if lock_hours else 0
        
        # Lock streak
        lock_streak = self._calculate_lock_streak(events)
        
        # Protection percentage
        protection_pct = (total_locked_items / total_items * 100) if total_items > 0 else 0
        
        # Last activity
        last_activity = None
        if events:
            last_event = events[-1]
            last_activity = {
                'type': last_event.get('event_type', 'unknown'),
                'item': last_event.get('item_name', 'N/A'),
                'timestamp': last_event.get('timestamp')
            }
        
        stats = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_items': total_items,
                'total_applications': total_apps,
                'total_locked_items': total_locked_items,
                'protection_percentage': round(protection_pct, 1),
                'lock_streak_days': lock_streak
            },
            'activity': {
                'total_lock_events': lock_events,
                'total_unlock_events': unlock_events,
                'failed_unlock_attempts': failed_attempts,
                'peak_lock_hour': peak_hour,
                'last_activity': last_activity
            },
            'items': {
                'most_locked': most_locked[:5],  # Top 5
                'total_unlock_count': total_locks
            }
        }
        
        return stats
    
    def _calculate_lock_streak(self, events: List[Dict]) -> int:
        """Calculate consecutive days with at least one lock event"""
        lock_dates = set()
        for event in events:
            if 'lock' in event.get('event_type', ''):
                try:
                    ts = datetime.fromisoformat(event['timestamp'])
                    lock_dates.add(ts.date())
                except:
                    pass
        
        if not lock_dates:
            return 0
        
        sorted_dates = sorted(lock_dates)
        streak = 1
        max_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] - sorted_dates[i-1] == timedelta(days=1):
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1
        
        # Check if current streak continues to today
        today = datetime.now().date()
        if sorted_dates[-1] == today or sorted_dates[-1] == today - timedelta(days=1):
            return max_streak
        return 0
    
    def get_stats(self, use_cache: bool = True) -> Dict:
        """Get statistics (use cache if valid)"""
        if use_cache and os.path.exists(self.stats_cache_file):
            try:
                with open(self.stats_cache_file, 'r') as f:
                    cached = json.load(f)
                # Check if cache is still fresh
                cache_time = datetime.fromisoformat(cached.get('generated_at', ''))
                if datetime.now() - cache_time < timedelta(seconds=self.cache_duration):
                    return cached
            except:
                pass
        
        # Calculate and cache
        stats = self.calculate_stats()
        try:
            with open(self.stats_cache_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except:
            pass
        
        return stats
    
    def get_pie_chart_data(self) -> Dict:
        """Get data for item type distribution pie chart with category items"""
        config = self._get_config()
        
        apps = config.get('applications', [])
        files_list = []
        folders_list = []
        
        for item in config.get('locked_files_and_folders', []):
            if item.get('type') == 'file':
                files_list.append(item)
            elif item.get('type') == 'folder':
                folders_list.append(item)
        
        # Build lists of names for each category
        app_names = [app.get('name', 'Unknown') for app in apps]
        file_names = [item.get('path', 'Unknown').split('/')[-1] for item in files_list]
        folder_names = [item.get('path', 'Unknown').split('/')[-1] for item in folders_list]
        
        return {
            'labels': ['Applications', 'Files', 'Folders'],
            'data': [len(apps), len(files_list), len(folders_list)],
            'category_items': {
                0: app_names,
                1: file_names,
                2: folder_names
            }
        }
    
    def get_lock_unlock_timeline(self, days: int = 7) -> Dict:
        """Get lock/unlock events over time for line chart"""
        events = self._get_activity_events()
        now = datetime.now()
        start_date = now - timedelta(days=days)
        
        # Group events by day and type
        timeline = defaultdict(lambda: {'locks': 0, 'unlocks': 0})
        
        for event in events:
            try:
                event_time = datetime.fromisoformat(event['timestamp'])
                if event_time >= start_date:
                    date_key = event_time.date().isoformat()
                    event_type = event.get('event_type', '').lower()
                    
                    if 'lock' in event_type and 'unlock' not in event_type:
                        timeline[date_key]['locks'] += 1
                    elif 'unlock' in event_type:
                        timeline[date_key]['unlocks'] += 1
            except:
                pass
        
        # Fill in missing dates with zeros
        all_dates = []
        for i in range(days, -1, -1):
            date = (now - timedelta(days=i)).date().isoformat()
            all_dates.append(date)
            if date not in timeline:
                timeline[date] = {'locks': 0, 'unlocks': 0}
        
        return {
            'dates': all_dates,
            'locks': [timeline[d]['locks'] for d in all_dates],
            'unlocks': [timeline[d]['unlocks'] for d in all_dates]
        }
    
    def get_duration_stats(self) -> Dict:
        """Calculate duration statistics from activity logs"""
        events = self._get_activity_events()
        
        # Find lock/unlock pairs to calculate durations
        item_sessions = defaultdict(list)
        
        for event in events:
            item_name = event.get('item_name', 'Unknown')
            event_type = event.get('event_type', '').lower()
            timestamp = event.get('timestamp')
            
            if item_name and timestamp:
                if 'lock' in event_type and 'unlock' not in event_type:
                    item_sessions[item_name].append({
                        'type': 'lock',
                        'timestamp': datetime.fromisoformat(timestamp)
                    })
                elif 'unlock' in event_type:
                    item_sessions[item_name].append({
                        'type': 'unlock',
                        'timestamp': datetime.fromisoformat(timestamp)
                    })
        
        # Calculate durations
        durations = {
            'by_item': {},
            'averages': {
                'avg_lock_duration_seconds': 0,
                'avg_unlock_duration_seconds': 0
            }
        }
        
        lock_durations = []
        unlock_durations = []
        
        for item_name, sessions in item_sessions.items():
            item_lock_durations = []
            item_unlock_durations = []
            
            sessions_sorted = sorted(sessions, key=lambda x: x['timestamp'])
            locked_since = None
            unlocked_since = None
            
            for session in sessions_sorted:
                if session['type'] == 'lock':
                    if unlocked_since:
                        # Calculate unlock duration
                        duration = (session['timestamp'] - unlocked_since).total_seconds()
                        item_unlock_durations.append(duration)
                        unlock_durations.append(duration)
                        unlocked_since = None
                    locked_since = session['timestamp']
                
                elif session['type'] == 'unlock':
                    if locked_since:
                        # Calculate lock duration
                        duration = (session['timestamp'] - locked_since).total_seconds()
                        item_lock_durations.append(duration)
                        lock_durations.append(duration)
                        locked_since = None
                    unlocked_since = session['timestamp']
            
            # Store item-specific stats
            avg_lock = sum(item_lock_durations) / len(item_lock_durations) if item_lock_durations else 0
            avg_unlock = sum(item_unlock_durations) / len(item_unlock_durations) if item_unlock_durations else 0
            
            durations['by_item'][item_name] = {
                'avg_lock_duration_seconds': round(avg_lock, 1),
                'avg_unlock_duration_seconds': round(avg_unlock, 1),
                'total_lock_sessions': len(item_lock_durations),
                'total_unlock_sessions': len(item_unlock_durations)
            }
        
        # Calculate overall averages
        if lock_durations:
            durations['averages']['avg_lock_duration_seconds'] = round(sum(lock_durations) / len(lock_durations), 1)
        if unlock_durations:
            durations['averages']['avg_unlock_duration_seconds'] = round(sum(unlock_durations) / len(unlock_durations), 1)
        
        return durations
    
    def get_comprehensive_stats(self) -> Dict:
        """Get all statistics including charts and durations"""
        base_stats = self.get_stats(use_cache=False)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'summary': base_stats.get('summary', {}),
            'activity': base_stats.get('activity', {}),
            'items': base_stats.get('items', {}),
            'pie_chart': self.get_pie_chart_data(),
            'timeline': self.get_lock_unlock_timeline(days=7),
            'durations': self.get_duration_stats(),
            'session_uptime': self.get_session_uptime()
        }
