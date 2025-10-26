"""
Performance Monitoring for OpenManus
This module implements performance monitoring to track response speed and latency improvements.
"""

import time
import logging
from typing import Dict, Any, List
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for tracking system performance"""
    timestamp: float
    response_time: float
    tokens_generated: int
    model_type: str
    input_length: int
    success: bool
    memory_usage_mb: float = 0.0

class PerformanceMonitor:
    """Monitor and track performance metrics for the OpenManus system"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.lock = Lock()
        self.start_time = time.time()
        
        # Performance counters
        self.request_count = 0
        self.total_response_time = 0.0
        self.successful_requests = 0
        
        logger.info("Performance Monitor initialized")
    
    def start_request(self) -> float:
        """Start timing a request and return the start time"""
        with self.lock:
            self.request_count += 1
            return time.time()
    
    def end_request(self, start_time: float, tokens_generated: int = 0, 
                   model_type: str = "unknown", input_length: int = 0, 
                   success: bool = True) -> float:
        """End timing a request and record metrics"""
        end_time = time.time()
        response_time = end_time - start_time
        
        # Get memory usage if possible
        memory_usage = 0.0
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except:
            pass
        
        # Create metrics record
        metrics = PerformanceMetrics(
            timestamp=end_time,
            response_time=response_time,
            tokens_generated=tokens_generated,
            model_type=model_type,
            input_length=input_length,
            success=success,
            memory_usage_mb=memory_usage
        )
        
        # Store metrics
        with self.lock:
            self.metrics_history.append(metrics)
            self.total_response_time += response_time
            if success:
                self.successful_requests += 1
        
        logger.info(f"Request completed: {response_time:.3f}s, {tokens_generated} tokens, {model_type}")
        return response_time
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics"""
        if not self.metrics_history:
            return {"message": "No metrics recorded yet"}
        
        with self.lock:
            # Calculate basic statistics
            total_requests = len(self.metrics_history)
            successful_requests = sum(1 for m in self.metrics_history if m.success)
            failed_requests = total_requests - successful_requests
            
            # Response time statistics
            response_times = [m.response_time for m in self.metrics_history]
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Throughput calculation (requests per second)
            time_span = self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp
            if time_span > 0:
                requests_per_second = total_requests / time_span
            else:
                requests_per_second = 0
            
            # Token generation statistics
            tokens_generated = [m.tokens_generated for m in self.metrics_history if m.tokens_generated > 0]
            if tokens_generated:
                avg_tokens_per_request = sum(tokens_generated) / len(tokens_generated)
                total_tokens = sum(tokens_generated)
                if avg_response_time > 0:
                    tokens_per_second = total_tokens / (avg_response_time * len(tokens_generated))
                else:
                    tokens_per_second = 0
            else:
                avg_tokens_per_request = 0
                total_tokens = 0
                tokens_per_second = 0
            
            # Model-specific statistics
            model_stats = defaultdict(list)
            for m in self.metrics_history:
                model_stats[m.model_type].append(m.response_time)
            
            model_performance = {}
            for model, times in model_stats.items():
                model_performance[model] = {
                    "count": len(times),
                    "avg_response_time": sum(times) / len(times),
                    "min_response_time": min(times),
                    "max_response_time": max(times)
                }
            
            # Memory usage statistics
            memory_usages = [m.memory_usage_mb for m in self.metrics_history if m.memory_usage_mb > 0]
            if memory_usages:
                avg_memory_usage = sum(memory_usages) / len(memory_usages)
                peak_memory_usage = max(memory_usages)
            else:
                avg_memory_usage = 0
                peak_memory_usage = 0
            
            return {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                "avg_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "requests_per_second": requests_per_second,
                "avg_tokens_per_request": avg_tokens_per_request,
                "total_tokens_generated": total_tokens,
                "tokens_per_second": tokens_per_second,
                "avg_memory_usage_mb": avg_memory_usage,
                "peak_memory_usage_mb": peak_memory_usage,
                "uptime_seconds": time.time() - self.start_time,
                "model_performance": model_performance
            }
    
    def get_recent_performance(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent performance metrics"""
        with self.lock:
            recent_metrics = list(self.metrics_history)[-count:]
            return [asdict(m) for m in recent_metrics]
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        with self.lock:
            self.metrics_history.clear()
            self.request_count = 0
            self.total_response_time = 0.0
            self.successful_requests = 0
            self.start_time = time.time()
            logger.info("Performance metrics reset")

# Global instance
performance_monitor = PerformanceMonitor()

def start_request_timer() -> float:
    """Start timing a request"""
    return performance_monitor.start_request()

def end_request_timer(start_time: float, tokens_generated: int = 0, 
                     model_type: str = "unknown", input_length: int = 0, 
                     success: bool = True) -> float:
    """End timing a request and record metrics"""
    return performance_monitor.end_request(
        start_time, tokens_generated, model_type, input_length, success
    )

def get_performance_report() -> Dict[str, Any]:
    """Get a performance report"""
    return performance_monitor.get_performance_summary()

def get_recent_metrics(count: int = 100) -> List[Dict[str, Any]]:
    """Get recent performance metrics"""
    return performance_monitor.get_recent_performance(count)