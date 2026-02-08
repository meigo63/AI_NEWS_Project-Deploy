"""
Performance metrics tracking service.
Measures inference time and CPU usage without blocking.
"""
import time
import psutil
from typing import Tuple


class MetricsTracker:
    """Lightweight metrics tracker for inference performance."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_cpu = None
        self.end_time = None
        self.end_cpu = None
    
    def start(self) -> None:
        """Start tracking metrics."""
        self.start_time = time.perf_counter()
        # Get CPU usage without interval (non-blocking)
        self.start_cpu = self.process.cpu_percent(interval=None)
    
    def stop(self) -> None:
        """Stop tracking metrics."""
        self.end_time = time.perf_counter()
        # Get CPU usage without interval (non-blocking)
        self.end_cpu = self.process.cpu_percent(interval=None)
    
    def get_processing_time_ms(self) -> float:
        """
        Get processing time in milliseconds.
        
        Returns:
            float: Processing time in milliseconds, or 0.0 if not tracked
        """
        if self.start_time is None or self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000  # Convert to ms
    
    def get_cpu_usage_percent(self) -> float:
        """
        Get average CPU usage percentage.
        
        Returns:
            float: Average CPU usage, or 0.0 if not tracked
        """
        if self.start_cpu is None or self.end_cpu is None:
            return 0.0
        # Return average of start and end measurements
        return (self.start_cpu + self.end_cpu) / 2
    
    def get_metrics(self) -> dict:
        """
        Get all metrics as a dictionary.
        
        Returns:
            dict: Dictionary containing processing_time_ms and cpu_usage_percent
        """
        return {
            'processing_time_ms': self.get_processing_time_ms(),
            'cpu_usage_percent': self.get_cpu_usage_percent()
        }
