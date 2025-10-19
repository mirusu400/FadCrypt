"""
Statistics Manager - Calculates and caches statistics
Parses config and activity logs to generate insights
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter


class StatisticsManager:
    """Manages statistics calculation and caching"""
    
    def __init__(self, config_folder: str):
        self.config_folder = config_folder
        self.config_file = os.path.join(config_folder, 'apps_config.json')
        self.activity_log_file = os.path.join(config_folder, 'activity.log')
        self.stats_cache_file = os.path.join(config_folder, 'statistics.json')
        self.cache_duration = 60  # seconds - recalculate if older than this
        
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
        
        # Most locked items
        most_locked = sorted(
            [(app['name'], app.get('unlock_count', 0)) for app in apps] +
            [(item['name'], item.get('unlock_count', 0)) for item in locked_items],
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
