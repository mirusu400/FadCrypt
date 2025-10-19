"""
Activity Manager - Tracks all lock/unlock events and security actions
Append-only audit log for accountability
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class ActivityManager:
    """Manages activity logging for audit trail"""
    
    def __init__(self, config_folder: str):
        self.config_folder = config_folder
        self.activity_log_file = os.path.join(config_folder, 'activity.log')
        self.max_file_size = 10 * 1024 * 1024  # 10MB before rotation
        
    def _rotate_log_if_needed(self):
        """Rotate log file if it exceeds max size"""
        if os.path.exists(self.activity_log_file):
            if os.path.getsize(self.activity_log_file) > self.max_file_size:
                backup_file = f"{self.activity_log_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.activity_log_file, backup_file)
                print(f"📝 Activity log rotated to {backup_file}")
    
    def log_event(self, event_type: str, item_name: Optional[str] = None, item_type: Optional[str] = None,
                  success: bool = True, duration_locked: Optional[str] = None, 
                  unlock_method: Optional[str] = None, details: Optional[str] = None, **kwargs):
        """
        Log an event to activity log.
        
        Args:
            event_type: lock, unlock, lock_all, unlock_all, add_item, remove_item,
                       password_changed, config_import, config_export, failed_unlock,
                       process_blocked, process_killed, etc.
            item_name: Name of the item (app/file/folder)
            item_type: application, file, or folder
            success: Whether operation succeeded
            duration_locked: How long item was locked
            unlock_method: password, recovery_code, admin_override
            details: Additional details
        """
        self._rotate_log_if_needed()
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'item_name': item_name,
            'item_type': item_type,
            'success': success,
            'duration_locked': duration_locked,
            'unlock_method': unlock_method,
            'details': details,
            **kwargs
        }
        
        try:
            with open(self.activity_log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
            print(f"📝 Activity logged: {event_type}")
        except Exception as e:
            print(f"❌ Error logging activity: {e}")
    
    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """Get most recent events"""
        if not os.path.exists(self.activity_log_file):
            return []
        
        try:
            events = []
            with open(self.activity_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
            return events[-limit:]  # Last N events
        except Exception as e:
            print(f"❌ Error reading activity log: {e}")
            return []
    
    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """Get all events of specific type"""
        events = self.get_recent_events(limit=1000)
        return [e for e in events if e.get('event_type') == event_type]
    
    def search_events(self, query: str) -> List[Dict]:
        """Search events by item name or details"""
        events = self.get_recent_events(limit=1000)
        query_lower = query.lower()
        return [e for e in events if 
                (e.get('item_name', '').lower().find(query_lower) >= 0 or
                 e.get('details', '').lower().find(query_lower) >= 0)]
    
    def export_to_csv(self, output_file: str) -> bool:
        """Export activity log to CSV"""
        import csv
        try:
            events = self.get_recent_events(limit=10000)
            if not events:
                print("No events to export")
                return False
            
            keys = set()
            for event in events:
                keys.update(event.keys())
            keys = sorted(list(keys))
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(events)
            
            print(f"✅ Activity log exported to {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error exporting activity log: {e}")
            return False
