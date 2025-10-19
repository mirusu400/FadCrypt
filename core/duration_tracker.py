"""Duration Tracker - Tracks how long items are locked/unlocked"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class DurationTracker:
    """Tracks duration of lock/unlock states for items"""
    
    def __init__(self, config_folder: str):
        self.config_folder = config_folder
        self.duration_file = os.path.join(config_folder, 'durations.json')
        self.current_sessions = {}  # item_name -> {'state': 'locked'/'unlocked', 'start_time': timestamp}
    
    def start_session(self, item_name: str, state: str = 'locked'):
        """Start tracking a lock or unlock session"""
        self.current_sessions[item_name] = {
            'state': state,
            'start_time': datetime.now().isoformat(),
            'duration_seconds': 0
        }
    
    def end_session(self, item_name: str) -> Optional[Dict]:
        """End tracking session and calculate duration"""
        if item_name not in self.current_sessions:
            return None
        
        session = self.current_sessions[item_name]
        start = datetime.fromisoformat(session['start_time'])
        end = datetime.now()
        duration_seconds = int((end - start).total_seconds())
        
        # Save duration
        durations = self._load_durations()
        if item_name not in durations:
            durations[item_name] = {'locked_seconds': 0, 'unlocked_seconds': 0, 'sessions': []}
        
        session_record = {
            'state': session['state'],
            'start': session['start_time'],
            'end': end.isoformat(),
            'duration_seconds': duration_seconds
        }
        durations[item_name]['sessions'].append(session_record)
        
        if session['state'] == 'locked':
            durations[item_name]['locked_seconds'] += duration_seconds
        else:
            durations[item_name]['unlocked_seconds'] += duration_seconds
        
        self._save_durations(durations)
        del self.current_sessions[item_name]
        
        return session_record
    
    def get_item_durations(self, item_name: str) -> Dict:
        """Get total and average durations for an item"""
        durations = self._load_durations()
        
        if item_name not in durations:
            return {
                'locked_seconds': 0,
                'unlocked_seconds': 0,
                'locked_hours': 0,
                'unlocked_hours': 0,
                'total_sessions': 0
            }
        
        item_data = durations[item_name]
        total_sessions = len(item_data.get('sessions', []))
        locked_seconds = item_data.get('locked_seconds', 0)
        unlocked_seconds = item_data.get('unlocked_seconds', 0)
        
        return {
            'locked_seconds': locked_seconds,
            'unlocked_seconds': unlocked_seconds,
            'locked_hours': locked_seconds / 3600,
            'unlocked_hours': unlocked_seconds / 3600,
            'total_sessions': total_sessions,
            'average_lock_duration': locked_seconds / max(1, total_sessions // 2)
        }
    
    def get_all_durations(self) -> Dict:
        """Get all durations"""
        return self._load_durations()
    
    def _load_durations(self) -> Dict:
        """Load durations from file"""
        if os.path.exists(self.duration_file):
            try:
                with open(self.duration_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_durations(self, durations: Dict):
        """Save durations to file"""
        try:
            with open(self.duration_file, 'w') as f:
                json.dump(durations, f, indent=4)
        except Exception as e:
            print(f"Error saving durations: {e}")
    
    def get_uptime_seconds(self) -> int:
        """Get FadCrypt uptime in seconds since first startup"""
        metadata_file = os.path.join(self.config_folder, 'metadata.json')
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    start_time = datetime.fromisoformat(metadata.get('first_startup', datetime.now().isoformat()))
                    uptime = int((datetime.now() - start_time).total_seconds())
                    return uptime
            except:
                pass
        
        # Create metadata if it doesn't exist
        metadata = {'first_startup': datetime.now().isoformat()}
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
        except:
            pass
        
        return 0
