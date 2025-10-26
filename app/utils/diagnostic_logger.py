"""
Diagnostic Logger for OpenManus
This module provides comprehensive diagnostic logging and feedback mechanisms for the AI agent platform.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

class DiagnosticLevel(Enum):
    """Enumeration of diagnostic levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    CRITICAL = "critical"

class DiagnosticLogger:
    """Comprehensive diagnostic logger for agent operations"""
    
    def __init__(self, log_file: str = "diagnostics.log"):
        """Initialize the diagnostic logger"""
        self.log_file = log_file
        self.diagnostics = []
        
        # Set up file logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Also set up console logging for critical issues
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
    
    def log_diagnostic(self, level: DiagnosticLevel, message: str, 
                      details: Optional[Dict[str, Any]] = None, 
                      component: str = "unknown") -> None:
        """
        Log a diagnostic message with optional details
        
        Args:
            level: Diagnostic level (INFO, WARNING, ERROR, etc.)
            message: Diagnostic message
            details: Optional dictionary with additional details
            component: Component that generated the diagnostic
        """
        timestamp = datetime.now().isoformat()
        
        diagnostic_entry = {
            "timestamp": timestamp,
            "level": level.value,
            "component": component,
            "message": message,
            "details": details or {}
        }
        
        # Add to in-memory diagnostics
        self.diagnostics.append(diagnostic_entry)
        
        # Log to file
        log_message = f"[{component}] {message}"
        if details:
            log_message += f" | Details: {json.dumps(details, indent=2)}"
        
        # Use appropriate logging level
        logger = logging.getLogger()
        if level == DiagnosticLevel.DEBUG:
            logger.debug(log_message)
        elif level == DiagnosticLevel.INFO:
            logger.info(log_message)
        elif level == DiagnosticLevel.WARNING:
            logger.warning(log_message)
        elif level == DiagnosticLevel.ERROR:
            logger.error(log_message)
        elif level == DiagnosticLevel.CRITICAL:
            logger.critical(log_message)
    
    def log_query_processing(self, query: str, analysis: Dict[str, Any], 
                           response: str, processing_time: float) -> None:
        """
        Log query processing details
        
        Args:
            query: Original user query
            analysis: Query analysis results
            response: Generated response
            processing_time: Time taken to process query
        """
        details = {
            "query": query,
            "analysis": analysis,
            "response_length": len(response),
            "processing_time_seconds": processing_time
        }
        
        self.log_diagnostic(
            DiagnosticLevel.INFO,
            f"Processed query: {query[:50]}...",
            details,
            "query_processor"
        )
    
    def log_tool_usage(self, tool_name: str, parameters: Dict[str, Any], 
                      result: Dict[str, Any], execution_time: float) -> None:
        """
        Log tool usage details
        
        Args:
            tool_name: Name of the tool used
            parameters: Tool parameters
            result: Tool execution result
            execution_time: Time taken to execute tool
        """
        details = {
            "tool_name": tool_name,
            "parameters": parameters,
            "result_summary": {
                "success": result.get("success", False),
                "error": result.get("error"),
                "observation_length": len(str(result.get("observation", "")))
            },
            "execution_time_seconds": execution_time
        }
        
        self.log_diagnostic(
            DiagnosticLevel.INFO,
            f"Used tool: {tool_name}",
            details,
            "tool_executor"
        )
    
    def log_model_interaction(self, model_type: str, prompt: str, 
                            response: str, tokens_used: int) -> None:
        """
        Log model interaction details
        
        Args:
            model_type: Type of model used
            prompt: Input prompt
            response: Model response
            tokens_used: Number of tokens used
        """
        details = {
            "model_type": model_type,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "tokens_used": tokens_used
        }
        
        self.log_diagnostic(
            DiagnosticLevel.DEBUG,
            f"Model interaction with {model_type}",
            details,
            "model_handler"
        )
    
    def log_error(self, component: str, error: Exception, 
                 context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error with full context
        
        Args:
            component: Component where error occurred
            error: Exception object
            context: Additional context information
        """
        details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        self.log_diagnostic(
            DiagnosticLevel.ERROR,
            f"Error in {component}: {str(error)}",
            details,
            component
        )
    
    def get_recent_diagnostics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent diagnostic entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent diagnostic entries
        """
        return self.diagnostics[-limit:] if self.diagnostics else []
    
    def get_diagnostics_by_level(self, level: DiagnosticLevel) -> List[Dict[str, Any]]:
        """
        Get diagnostics filtered by level
        
        Args:
            level: Diagnostic level to filter by
            
        Returns:
            List of diagnostics with specified level
        """
        return [d for d in self.diagnostics if d["level"] == level.value]
    
    def clear_diagnostics(self) -> None:
        """Clear all stored diagnostics"""
        self.diagnostics.clear()
    
    def generate_diagnostic_report(self) -> str:
        """
        Generate a comprehensive diagnostic report
        
        Returns:
            Formatted diagnostic report
        """
        if not self.diagnostics:
            return "No diagnostics available."
        
        report = "🔍 OpenManus Diagnostic Report\n"
        report += "=" * 40 + "\n\n"
        
        # Summary statistics
        total_diagnostics = len(self.diagnostics)
        levels = [d["level"] for d in self.diagnostics]
        level_counts = {level: levels.count(level) for level in set(levels)}
        
        report += f"Total Diagnostics: {total_diagnostics}\n"
        for level, count in level_counts.items():
            report += f"{level.capitalize()}: {count}\n"
        
        report += "\nRecent Diagnostics:\n"
        report += "-" * 20 + "\n"
        
        # Last 10 diagnostics
        for diag in self.diagnostics[-10:]:
            report += f"[{diag['timestamp']}] {diag['level'].upper()} - {diag['component']}: {diag['message']}\n"
            if diag['details']:
                report += f"  Details: {json.dumps(diag['details'], indent=2)[:200]}...\n"
            report += "\n"
        
        return report

# Global instance
diagnostic_logger = DiagnosticLogger()

def log_query_processing(query: str, analysis: Dict[str, Any], 
                        response: str, processing_time: float) -> None:
    """Log query processing details"""
    diagnostic_logger.log_query_processing(query, analysis, response, processing_time)

def log_tool_usage(tool_name: str, parameters: Dict[str, Any], 
                  result: Dict[str, Any], execution_time: float) -> None:
    """Log tool usage details"""
    diagnostic_logger.log_tool_usage(tool_name, parameters, result, execution_time)

def log_model_interaction(model_type: str, prompt: str, 
                         response: str, tokens_used: int) -> None:
    """Log model interaction details"""
    diagnostic_logger.log_model_interaction(model_type, prompt, response, tokens_used)

def log_error(component: str, error: Exception, 
             context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with full context"""
    diagnostic_logger.log_error(component, error, context)

def get_recent_diagnostics(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent diagnostic entries"""
    return diagnostic_logger.get_recent_diagnostics(limit)

def generate_diagnostic_report() -> str:
    """Generate a comprehensive diagnostic report"""
    return diagnostic_logger.generate_diagnostic_report()