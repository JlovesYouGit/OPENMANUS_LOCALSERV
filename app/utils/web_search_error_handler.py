"""
Enhanced Web Search Error Handling with Better Fallback Mechanisms
This module implements improved error handling and fallback mechanisms for web search operations.
"""

import asyncio
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class SearchEngineStatus:
    """Status information for a search engine"""
    name: str
    is_available: bool = True
    last_error: Optional[str] = None
    error_count: int = 0
    last_checked: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    
    def should_retry(self) -> bool:
        """Check if we should retry this engine"""
        if not self.is_available:
            # Check if cooldown period has expired
            if self.cooldown_until and datetime.now() >= self.cooldown_until:
                return True
            return False
        return True
    
    def apply_cooldown(self, minutes: int = 5):
        """Apply a cooldown period after repeated failures"""
        self.cooldown_until = datetime.now() + timedelta(minutes=minutes)
        self.is_available = False

class WebSearchErrorHandler:
    """Enhanced error handler for web search operations"""
    
    def __init__(self):
        self.engine_status: Dict[str, SearchEngineStatus] = {}
        self.max_error_count = 3
        self.default_cooldown = 5  # minutes
        
    def register_engine(self, engine_name: str):
        """Register a search engine"""
        if engine_name not in self.engine_status:
            self.engine_status[engine_name] = SearchEngineStatus(name=engine_name)
    
    def report_success(self, engine_name: str):
        """Report successful search operation"""
        if engine_name in self.engine_status:
            status = self.engine_status[engine_name]
            status.is_available = True
            status.last_error = None
            status.error_count = 0
            status.last_checked = datetime.now()
            status.cooldown_until = None
    
    def report_error(self, engine_name: str, error: str):
        """Report failed search operation"""
        self.register_engine(engine_name)  # Ensure engine is registered
        
        status = self.engine_status[engine_name]
        status.is_available = False
        status.last_error = error
        status.error_count += 1
        status.last_checked = datetime.now()
        
        # Apply cooldown if error count exceeds threshold
        if status.error_count >= self.max_error_count:
            status.apply_cooldown(self.default_cooldown)
    
    def get_available_engines(self, engine_order: List[str]) -> List[str]:
        """Get list of available engines in preferred order"""
        available = []
        for engine_name in engine_order:
            self.register_engine(engine_name)  # Ensure engine is registered
            status = self.engine_status[engine_name]
            if status.should_retry():
                available.append(engine_name)
        return available
    
    def get_error_message(self, engine_name: str, error: str) -> str:
        """Generate user-friendly error message"""
        status = self.engine_status.get(engine_name)
        if status and status.error_count > 1:
            return f"Search engine '{engine_name}' is temporarily unavailable due to repeated errors. Error: {error}. Please try again later or use a different search query."
        elif "DuckDuckGoSearchException" in error:
            return f"Temporary issue with DuckDuckGo search. This often resolves itself. Error: {error}"
        elif "timeout" in error.lower():
            return f"Search operation timed out. This may be due to network issues or high server load. Error: {error}"
        else:
            return f"Search encountered an issue: {error}. This may be temporary."
    
    def get_fallback_suggestion(self, failed_engines: List[str]) -> str:
        """Generate fallback suggestion for users"""
        if not failed_engines:
            return ""
        
        suggestion = "I tried searching with "
        if len(failed_engines) == 1:
            suggestion += f"{failed_engines[0]}"
        else:
            suggestion += ", ".join(failed_engines[:-1]) + f" and {failed_engines[-1]}"
        
        suggestion += ", but encountered issues. "
        
        # Suggest alternatives
        working_engines = [name for name, status in self.engine_status.items() 
                          if status.is_available and name not in failed_engines]
        
        if working_engines:
            if len(working_engines) == 1:
                suggestion += f"You could try searching with {working_engines[0]}."
            else:
                suggestion += f"You could try searching with {', '.join(working_engines[:-1])} or {working_engines[-1]}."
        else:
            suggestion += "Please try again later when the search services are restored."
        
        return suggestion
    
    def log_error_details(self, engine_name: str, query: str, error: str):
        """Log detailed error information for debugging"""
        print(f"[ERROR] Search failed - Engine: {engine_name}, Query: {query}")
        print(f"[ERROR] Detailed error: {error}")
        if engine_name in self.engine_status:
            status = self.engine_status[engine_name]
            print(f"[ERROR] Engine status - Available: {status.is_available}, Error count: {status.error_count}")

# Global instance
search_error_handler = WebSearchErrorHandler()

def handle_search_error(engine_name: str, query: str, error: str) -> Dict[str, Any]:
    """
    Handle search error with enhanced error reporting and fallback suggestions
    
    Args:
        engine_name: Name of the search engine that failed
        query: The search query
        error: The error message
        
    Returns:
        Dictionary with error handling information
    """
    # Report the error
    search_error_handler.report_error(engine_name, error)
    
    # Log detailed error information
    search_error_handler.log_error_details(engine_name, query, error)
    
    # Generate user-friendly error message
    user_message = search_error_handler.get_error_message(engine_name, error)
    
    # Generate fallback suggestion
    failed_engines = [engine_name]  # In a real implementation, this would track all failed engines
    fallback_suggestion = search_error_handler.get_fallback_suggestion(failed_engines)
    
    return {
        "user_message": user_message,
        "fallback_suggestion": fallback_suggestion,
        "should_retry": search_error_handler.engine_status[engine_name].should_retry(),
        "retry_after": search_error_handler.engine_status[engine_name].cooldown_until
    }

async def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Retry a function with exponential backoff
    
    Args:
        func: The function to retry
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
        
    Returns:
        Result of the function or raises the last exception
    """
    last_exception = Exception("No attempts made")
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed. Last error: {e}")
    
    raise last_exception