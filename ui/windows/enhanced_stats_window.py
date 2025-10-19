"""Enhanced Statistics Window - Beautiful dashboard with pie/line charts and duration metrics"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QGridLayout, QFrame, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import QSize
import pyqtgraph as pg
import json


class EnhancedStatsWindow(QWidget):
    """Enhanced statistics dashboard with charts"""
    
    def __init__(self, statistics_manager=None, resource_path=None, parent=None):
        super().__init__(parent)
        self.statistics_manager = statistics_manager
        self.resource_path = resource_path or self._default_resource_path
        
        # Enable antialiasing for better chart quality
        pg.setConfigOption('antialias', True)
        
        self.init_ui()
        
        # Auto-refresh every 60 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(60000)
    
    def _default_resource_path(self, path):
        return path
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("FadCrypt Statistics & Analytics")
        self.setGeometry(100, 100, 1200, 800)
        
        # Dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
            }
            QTabWidget {
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 8px 20px;
            }
            QTabBar::tab:selected {
                background-color: #FF6B6B;
                color: white;
            }
            QScrollArea {
                border: none;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Title
        title = QLabel("📊 FadCrypt Security Analytics")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setStyleSheet("color: #444;")
        main_layout.addWidget(sep)
        
        # Tab widget for different views
        tabs = QTabWidget()
        
        # Overview Tab
        overview_widget = self._create_overview_tab()
        tabs.addTab(overview_widget, "Overview")
        
        # Charts Tab
        charts_widget = self._create_charts_tab()
        tabs.addTab(charts_widget, "Charts & Trends")
        
        # Duration Stats Tab
        duration_widget = self._create_duration_tab()
        tabs.addTab(duration_widget, "Duration Statistics")
        
        # System Info Tab
        system_widget = self._create_system_tab()
        tabs.addTab(system_widget, "System Information")
        
        main_layout.addWidget(tabs, 1)
        
        # Refresh button at bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh Now")
        refresh_btn.setMaximumWidth(200)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_stats)
        button_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(button_layout)
        
        self.refresh_stats()
    
    def _create_overview_tab(self) -> QWidget:
        """Create overview tab with key metrics"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Metric cards in grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Top metrics row
        self.metric_cards = {}
        
        # Protection %
        card1 = self._create_metric_card("🛡️ Protection Level", "0%", 
                                        "Percentage of items currently protected/locked")
        self.metric_cards['protection'] = card1
        grid.addWidget(card1, 0, 0)
        
        # Total items
        card2 = self._create_metric_card("📦 Total Items", "0",
                                        "Total count of all applications and locked files/folders")
        self.metric_cards['total_items'] = card2
        grid.addWidget(card2, 0, 1)
        
        # Lock Events
        card3 = self._create_metric_card("🔒 Lock Events", "0",
                                        "Total number of lock operations performed")
        self.metric_cards['lock_events'] = card3
        grid.addWidget(card3, 0, 2)
        
        # Unlock Events
        card4 = self._create_metric_card("🔓 Unlock Events", "0",
                                        "Total number of unlock operations performed")
        self.metric_cards['unlock_events'] = card4
        grid.addWidget(card4, 0, 3)
        
        # Uptime
        card5 = self._create_metric_card("⏱️ FadCrypt Uptime", "0h 0m",
                                        "How long FadCrypt has been running since first startup")
        self.metric_cards['uptime'] = card5
        grid.addWidget(card5, 1, 0)
        
        # Avg Lock Duration
        card6 = self._create_metric_card("⌛ Avg Lock Duration", "0s",
                                        "Average amount of time items spend in locked state")
        self.metric_cards['avg_lock_duration'] = card6
        grid.addWidget(card6, 1, 1)
        
        # Peak Hour
        card7 = self._create_metric_card("📈 Peak Lock Hour", "N/A",
                                        "The hour of day (0-23) with most lock activity")
        self.metric_cards['peak_hour'] = card7
        grid.addWidget(card7, 1, 2)
        
        # Failed Attempts
        card8 = self._create_metric_card("⚠️ Failed Attempts", "0",
                                        "Number of failed unlock attempts")
        self.metric_cards['failed_attempts'] = card8
        grid.addWidget(card8, 1, 3)
        
        content_layout.addLayout(grid)
        
        # Most locked items section
        content_layout.addSpacing(20)
        most_locked_label = QLabel("📊 Most Locked Items")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        most_locked_label.setFont(font)
        content_layout.addWidget(most_locked_label)
        
        self.most_locked_widget = QLabel("Loading...")
        self.most_locked_widget.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                padding: 15px;
                border-radius: 4px;
                color: #b0b0b0;
            }
        """)
        content_layout.addWidget(self.most_locked_widget)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_charts_tab(self) -> QWidget:
        """Create charts visualization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Info text
        info_text = QLabel("ℹ️ Visual Analytics\nPie chart shows distribution of protected items by type. Line chart shows 7-day activity trend.")
        info_text.setStyleSheet("color: #999; padding: 10px; background-color: #2a2a2a; border-radius: 4px;")
        layout.addWidget(info_text)
        layout.addSpacing(10)
        
        # Horizontal layout for charts
        charts_layout = QHBoxLayout()
        
        # Pie chart - item type distribution
        pie_label = QLabel("Item Type Distribution")
        pie_font = QFont()
        pie_font.setPointSize(12)
        pie_font.setBold(True)
        pie_label.setFont(pie_font)
        
        self.pie_chart = pg.PlotWidget(title="Item Types")
        self.pie_chart.setLabel('left', '')
        self.pie_chart.setLabel('bottom', '')
        self.pie_chart.showGrid(False, False)
        self.pie_chart.setMouseEnabled(x=False, y=False)
        
        pie_container = QVBoxLayout()
        pie_container.addWidget(pie_label)
        pie_container.addWidget(self.pie_chart)
        charts_layout.addLayout(pie_container)
        
        # Line chart - lock/unlock timeline
        timeline_label = QLabel("Lock/Unlock Timeline (7 days)")
        timeline_font = QFont()
        timeline_font.setPointSize(12)
        timeline_font.setBold(True)
        timeline_label.setFont(timeline_font)
        
        self.line_chart = pg.PlotWidget(title="Activity Timeline")
        self.line_chart.setLabel('left', 'Events')
        self.line_chart.setLabel('bottom', 'Date')
        self.line_chart.showGrid(True, True)
        self.line_chart.setMouseEnabled(x=False, y=False)
        
        timeline_container = QVBoxLayout()
        timeline_container.addWidget(timeline_label)
        timeline_container.addWidget(self.line_chart)
        charts_layout.addLayout(timeline_container)
        
        layout.addLayout(charts_layout)
        return widget
    
    def _create_duration_tab(self) -> QWidget:
        """Create duration statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Info text
        info_text = QLabel("ℹ️ Duration Statistics\nThis tab shows timing information about how long items are locked or unlocked")
        info_text.setStyleSheet("color: #999; padding: 10px; background-color: #2a2a2a; border-radius: 4px;")
        content_layout.addWidget(info_text)
        content_layout.addSpacing(10)
        
        # Duration summary
        summary_label = QLabel("⏳ Duration Summary")
        summary_font = QFont()
        summary_font.setPointSize(14)
        summary_font.setBold(True)
        summary_label.setFont(summary_font)
        content_layout.addWidget(summary_label)
        
        # Duration cards
        grid = QGridLayout()
        grid.setSpacing(15)
        
        self.duration_cards = {}
        
        card1 = self._create_metric_card("⌛ Avg Lock Duration", "N/A",
                                        "Average time items remain in locked state")
        self.duration_cards['avg_lock'] = card1
        grid.addWidget(card1, 0, 0)
        
        card2 = self._create_metric_card("🔓 Avg Unlock Duration", "N/A",
                                        "Average time between locks (time items stay unlocked)")
        self.duration_cards['avg_unlock'] = card2
        grid.addWidget(card2, 0, 1)
        
        card3 = self._create_metric_card("🕐 Total Locked Time", "N/A",
                                        "Cumulative time all items have been locked")
        self.duration_cards['total_locked'] = card3
        grid.addWidget(card3, 0, 2)
        
        card4 = self._create_metric_card("🕑 Total Unlocked Time", "N/A",
                                        "Cumulative time all items have been unlocked")
        self.duration_cards['total_unlocked'] = card4
        grid.addWidget(card4, 0, 3)
        
        content_layout.addLayout(grid)
        
        # Per-item durations
        content_layout.addSpacing(20)
        items_label = QLabel("📋 Per-Item Duration Stats")
        items_font = QFont()
        items_font.setPointSize(12)
        items_font.setBold(True)
        items_label.setFont(items_font)
        content_layout.addWidget(items_label)
        
        self.duration_items_widget = QLabel("Loading...")
        self.duration_items_widget.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                padding: 15px;
                border-radius: 4px;
                color: #b0b0b0;
                font-family: monospace;
            }
        """)
        self.duration_items_widget.setWordWrap(True)
        content_layout.addWidget(self.duration_items_widget)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_system_tab(self) -> QWidget:
        """Create system information tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Info text
        info_text = QLabel("ℹ️ System & Session Information\nMetadata about FadCrypt's current session and cache status")
        info_text.setStyleSheet("color: #999; padding: 10px; background-color: #2a2a2a; border-radius: 4px;")
        content_layout.addWidget(info_text)
        content_layout.addSpacing(10)
        
        title = QLabel("Session Details")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        content_layout.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        self.system_cards = {}
        
        card1 = self._create_metric_card("🚀 Session Start", "N/A",
                                        "Timestamp when FadCrypt was first started")
        self.system_cards['session_start'] = card1
        grid.addWidget(card1, 0, 0)
        
        card2 = self._create_metric_card("⏱️ Session Duration", "N/A",
                                        "How long FadCrypt has been running")
        self.system_cards['session_duration'] = card2
        grid.addWidget(card2, 0, 1)
        
        card3 = self._create_metric_card("📅 Last Activity", "N/A",
                                        "Timestamp of the last lock/unlock operation")
        self.system_cards['last_activity'] = card3
        grid.addWidget(card3, 0, 2)
        
        card4 = self._create_metric_card("🔄 Cache Status", "Fresh",
                                        "Whether statistics cache is fresh or needs refresh")
        self.system_cards['cache_status'] = card4
        grid.addWidget(card4, 0, 3)
        
        content_layout.addLayout(grid)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_metric_card(self, title: str, value: str, tooltip: str = "") -> QFrame:
        """Create a metric display card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
        """)
        card.setMinimumHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #999;")
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet("color: #FF6B6B;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        # Add tooltip if provided
        if tooltip:
            card.setToolTip(tooltip)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def refresh_stats(self):
        """Refresh all statistics"""
        if not self.statistics_manager:
            return
        
        try:
            stats = self.statistics_manager.get_comprehensive_stats()
            self._update_overview(stats)
            self._update_charts(stats)
            self._update_duration_stats(stats)
            self._update_system_info(stats)
        except Exception as e:
            print(f"Error refreshing stats: {e}")
    
    def _update_overview(self, stats: dict):
        """Update overview tab metrics"""
        try:
            summary = stats.get('summary', {})
            activity = stats.get('activity', {})
            
            self.metric_cards['protection'].value_label.setText(
                f"{summary.get('protection_percentage', 0)}%"
            )
            self.metric_cards['total_items'].value_label.setText(
                str(summary.get('total_items', 0))
            )
            self.metric_cards['lock_events'].value_label.setText(
                str(activity.get('total_lock_events', 0))
            )
            self.metric_cards['unlock_events'].value_label.setText(
                str(activity.get('total_unlock_events', 0))
            )
            
            uptime = stats.get('session_uptime', {})
            uptime_str = uptime.get('uptime_formatted', 'N/A')
            self.metric_cards['uptime'].value_label.setText(uptime_str)
            
            durations = stats.get('durations', {})
            avg_lock = durations.get('averages', {}).get('avg_lock_duration_seconds', 0)
            self._format_duration_card(self.metric_cards['avg_lock_duration'], avg_lock)
            
            self.metric_cards['peak_hour'].value_label.setText(
                f"{activity.get('peak_lock_hour', 0)}:00"
            )
            self.metric_cards['failed_attempts'].value_label.setText(
                str(activity.get('failed_unlock_attempts', 0))
            )
            
            # Most locked items
            items = stats.get('items', {}).get('most_locked', [])
            items_text = "\n".join([f"• {item[0]}: {item[1]} times" for item in items[:5]]) if items else "No data yet"
            self.most_locked_widget.setText(items_text)
        except Exception as e:
            print(f"Error updating overview: {e}")
    
    def _update_charts(self, stats: dict):
        """Update pie and line charts"""
        try:
            # Pie chart - item type distribution
            pie_data = stats.get('pie_chart', {})
            labels = pie_data.get('labels', [])
            data = pie_data.get('data', [])
            
            if data and sum(data) > 0:
                self._draw_pie_chart(labels, data)
            
            # Line chart - timeline
            timeline = stats.get('timeline', {})
            dates = timeline.get('dates', [])
            locks = timeline.get('locks', [])
            unlocks = timeline.get('unlocks', [])
            
            if dates and (locks or unlocks):
                self._draw_line_chart(dates, locks, unlocks)
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def _draw_pie_chart(self, labels: list, data: list):
        """Draw pie chart (using bar representation in PyQtGraph)"""
        try:
            self.pie_chart.clear()
            
            # Ensure data is numeric and non-negative
            numeric_data = [max(0, float(d)) if d else 0 for d in data]
            
            # Skip if no data
            if not numeric_data or sum(numeric_data) == 0:
                self.pie_chart.addItem(pg.TextItem("No data available"))
                return
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            x = list(range(len(labels)))
            bar_graph = pg.BarGraphItem(x=x, height=numeric_data, width=0.6, brush=colors[:len(labels)])
            self.pie_chart.addItem(bar_graph)
            
            # Set x-axis labels
            ax = self.pie_chart.getAxis('bottom')
            ax.setTicks([[(i, label) for i, label in enumerate(labels)]])
        except Exception as e:
            print(f"Error drawing pie chart: {e}")
    
    def _draw_line_chart(self, dates: list, locks: list, unlocks: list):
        """Draw line chart for lock/unlock timeline"""
        try:
            self.line_chart.clear()
            
            x = list(range(len(dates)))
            
            # Plot lock events
            lock_line = self.line_chart.plot(x, locks, pen=pg.mkPen('#FF6B6B', width=2), 
                                            name='Locks', symbol='o', symbolSize=8)
            
            # Plot unlock events
            unlock_line = self.line_chart.plot(x, unlocks, pen=pg.mkPen('#4ECDC4', width=2),
                                              name='Unlocks', symbol='s', symbolSize=8)
            
            # Add legend
            self.line_chart.addLegend()
            
            # Set x-axis labels (show every other date to avoid crowding)
            ax = self.line_chart.getAxis('bottom')
            ticks = []
            for i in range(0, len(dates), max(1, len(dates) // 4)):
                ticks.append((i, dates[i][-5:]))  # Show last 5 chars of date
            ax.setTicks([ticks])
        except Exception as e:
            print(f"Error drawing line chart: {e}")
    
    def _update_duration_stats(self, stats: dict):
        """Update duration statistics"""
        try:
            durations = stats.get('durations', {})
            averages = durations.get('averages', {})
            
            avg_lock = averages.get('avg_lock_duration_seconds', 0)
            avg_unlock = averages.get('avg_unlock_duration_seconds', 0)
            
            self._format_duration_card(self.duration_cards['avg_lock'], avg_lock)
            self._format_duration_card(self.duration_cards['avg_unlock'], avg_unlock)
            
            # Per-item stats
            by_item = durations.get('by_item', {})
            items_info = []
            
            for item_name, item_stats in list(by_item.items())[:10]:
                lock_sec = item_stats.get('avg_lock_duration_seconds', 0)
                unlock_sec = item_stats.get('avg_unlock_duration_seconds', 0)
                items_info.append(
                    f"{item_name}: Lock={self._format_seconds(lock_sec)}, Unlock={self._format_seconds(unlock_sec)}"
                )
            
            items_text = "\n".join(items_info) if items_info else "No duration data yet"
            self.duration_items_widget.setText(items_text)
        except Exception as e:
            print(f"Error updating duration stats: {e}")
    
    def _update_system_info(self, stats: dict):
        """Update system information tab"""
        try:
            uptime = stats.get('session_uptime', {})
            activity = stats.get('activity', {})
            
            start_time = uptime.get('first_startup', 'N/A')
            self.system_cards['session_start'].value_label.setText(start_time[:19])  # Date only
            
            self.system_cards['session_duration'].value_label.setText(
                uptime.get('uptime_formatted', 'N/A')
            )
            
            last_activity = activity.get('last_activity', {})
            if last_activity:
                timestamp = last_activity.get('timestamp', 'N/A')
                self.system_cards['last_activity'].value_label.setText(timestamp[:19])
            
            self.system_cards['cache_status'].value_label.setText("Fresh")
        except Exception as e:
            print(f"Error updating system info: {e}")
    
    @staticmethod
    def _format_duration_card(card: QFrame, seconds: float):
        """Format duration into human readable form"""
        card.value_label.setText(EnhancedStatsWindow._format_seconds(seconds))
    
    @staticmethod
    def _format_seconds(seconds: float) -> str:
        """Convert seconds to human readable format"""
        seconds = int(seconds)
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
