from datetime import date, timedelta
import numpy as np
from collections import defaultdict


class ActivityMap:
    """
    Base class for creating activity maps (similar to GitHub contribution graphs).
    """
    
    def __init__(self, reference_date=None):
        self.reference_date = reference_date or date.today()
        self.data = None
        self.activity_dates = set()
        
    def load_activity(self, activity_dates):
        """
        Load activity data from a list of dates.
        
        Args:
            activity_dates: List of date objects representing activity dates
        """
        self.activity_dates = set(activity_dates)
        self._build_data()
        
    def _build_data(self):
        """Build the activity data matrix."""
        # Create a 7x53 matrix (7 days of week, 53 weeks max)
        self.data = np.zeros((7, 53), dtype=int)
        
        # Calculate the start date (1 year ago from reference date)
        start_date = self.reference_date - timedelta(days=365)
        
        # Fill the matrix with activity data
        current_date = start_date
        week = 0
        
        while current_date <= self.reference_date and week < 53:
            day_of_week = current_date.weekday()
            if current_date in self.activity_dates:
                # Count activities for this date (simple count for now)
                self.data[day_of_week, week] = 1
            current_date += timedelta(days=1)
            
            # Move to next week if we've completed a week
            if current_date.weekday() == 0:  # Monday
                week += 1
                
    def get_data(self):
        """Return the activity data matrix."""
        return self.data
        
    def get_x_ticks(self):
        """Return x-axis tick labels (months)."""
        # Generate month labels for the x-axis
        months = []
        current_date = self.reference_date - timedelta(days=365)
        
        for i in range(12):
            month_date = current_date + timedelta(days=i * 30)
            months.append(month_date.strftime("%b"))
            
        return months
        
    def get_y_ticks(self):
        """Return y-axis tick labels (days of week)."""
        return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class SpanishActivityMap(ActivityMap):
    """
    Spanish version of ActivityMap with localized day and month names.
    """
    
    def get_x_ticks(self):
        """Return Spanish month abbreviations."""
        months = ["ene", "feb", "mar", "abr", "may", "jun", 
                 "jul", "ago", "sep", "oct", "nov", "dic"]
        return months
        
    def get_y_ticks(self):
        """Return Spanish day abbreviations."""
        return ["lun", "mar", "mie", "jue", "vie", "sab", "dom"]
