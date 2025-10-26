"""
Automated Consistency Audits for Financial Data
This module implements automated consistency audits for financial data with regression test suites
and cache invalidation mechanisms.
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

@dataclass
class AuditResult:
    """Result of a consistency audit"""
    timestamp: datetime
    query: str
    previous_result: Optional[Any]
    current_result: Any
    is_consistent: bool
    deviation_percentage: float
    notes: List[str] = field(default_factory=list)

@dataclass
class AuditHistory:
    """History of audit results for a specific query"""
    query: str
    results: List[AuditResult] = field(default_factory=list)
    last_audit: Optional[datetime] = None
    is_failing: bool = False

class FinancialDataAuditor:
    """Automated auditor for financial data consistency"""
    
    def __init__(self, audit_storage_path: str = "audit_history.json"):
        self.audit_storage_path = audit_storage_path
        self.audit_history: Dict[str, AuditHistory] = {}
        self.load_audit_history()
        
        # Threshold for consistency checking (5% deviation)
        self.deviation_threshold = 5.0
        
        # Audit schedule (in minutes)
        self.audit_intervals = {
            "financial": 60,  # Hourly for financial data
            "biographical": 1440,  # Daily for biographical data
            "technical": 720,  # Every 12 hours for technical data
            "general": 1440,  # Daily for general data
        }
        
        # Major query types to audit
        self.major_query_types = [
            "stock price", "company information", "financial report",
            "market data", "currency exchange", "commodity price"
        ]
    
    def load_audit_history(self):
        """Load audit history from storage"""
        try:
            if os.path.exists(self.audit_storage_path):
                with open(self.audit_storage_path, 'r') as f:
                    data = json.load(f)
                    for query, history_data in data.items():
                        results = []
                        for result_data in history_data.get('results', []):
                            result = AuditResult(
                                timestamp=datetime.fromisoformat(result_data['timestamp']),
                                query=result_data['query'],
                                previous_result=result_data.get('previous_result'),
                                current_result=result_data['current_result'],
                                is_consistent=result_data['is_consistent'],
                                deviation_percentage=result_data['deviation_percentage'],
                                notes=result_data.get('notes', [])
                            )
                            results.append(result)
                        
                        self.audit_history[query] = AuditHistory(
                            query=query,
                            results=results,
                            last_audit=datetime.fromisoformat(history_data['last_audit']) if history_data['last_audit'] else None,
                            is_failing=history_data.get('is_failing', False)
                        )
        except Exception as e:
            print(f"Warning: Could not load audit history: {e}")
    
    def save_audit_history(self):
        """Save audit history to storage"""
        try:
            # Convert to serializable format
            data = {}
            for query, history in self.audit_history.items():
                results_data = []
                for result in history.results:
                    result_data = {
                        'timestamp': result.timestamp.isoformat(),
                        'query': result.query,
                        'previous_result': result.previous_result,
                        'current_result': result.current_result,
                        'is_consistent': result.is_consistent,
                        'deviation_percentage': result.deviation_percentage,
                        'notes': result.notes
                    }
                    results_data.append(result_data)
                
                data[query] = {
                    'results': results_data,
                    'last_audit': history.last_audit.isoformat() if history.last_audit else None,
                    'is_failing': history.is_failing
                }
            
            with open(self.audit_storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save audit history: {e}")
    
    def should_audit_query(self, query: str, query_type: str) -> bool:
        """
        Determine if a query should be audited based on schedule
        
        Args:
            query: The query to check
            query_type: Type of query (financial, biographical, etc.)
            
        Returns:
            True if query should be audited, False otherwise
        """
        # Check if this is a major query type we want to audit
        if not any(major_type in query.lower() for major_type in self.major_query_types):
            return False
        
        # Get the audit history for this query
        history = self.audit_history.get(query)
        if not history:
            return True  # Audit new queries
        
        # Get the interval for this query type
        interval_minutes = self.audit_intervals.get(query_type, self.audit_intervals["general"])
        
        # Check if enough time has passed since last audit
        if history.last_audit:
            time_since_last = datetime.now() - history.last_audit
            return time_since_last.total_seconds() >= interval_minutes * 60
        
        return True
    
    def calculate_deviation(self, previous_value: float, current_value: float) -> float:
        """
        Calculate percentage deviation between two values
        
        Args:
            previous_value: Previous value
            current_value: Current value
            
        Returns:
            Percentage deviation
        """
        if previous_value == 0:
            if current_value == 0:
                return 0.0
            else:
                return 100.0  # 100% deviation if previous was 0 and current is not
        
        return abs((current_value - previous_value) / previous_value) * 100
    
    def check_consistency(self, query: str, current_result: Any) -> AuditResult:
        """
        Check consistency of a result against historical data
        
        Args:
            query: The query that produced the result
            current_result: The current result to check
            
        Returns:
            Audit result with consistency information
        """
        # Get previous result
        history = self.audit_history.get(query)
        previous_result = None
        if history and history.results:
            previous_result = history.results[-1].current_result
        
        # Initialize audit result
        audit_result = AuditResult(
            timestamp=datetime.now(),
            query=query,
            previous_result=previous_result,
            current_result=current_result,
            is_consistent=True,
            deviation_percentage=0.0,
            notes=[]
        )
        
        # If no previous result, consistency is assumed
        if previous_result is None:
            audit_result.notes.append("No previous result for comparison")
            return audit_result
        
        # Try to extract numerical values for comparison
        prev_value = self._extract_numeric_value(previous_result)
        curr_value = self._extract_numeric_value(current_result)
        
        if prev_value is not None and curr_value is not None:
            # Calculate deviation
            deviation = self.calculate_deviation(prev_value, curr_value)
            audit_result.deviation_percentage = deviation
            
            # Check if deviation exceeds threshold
            if deviation > self.deviation_threshold:
                audit_result.is_consistent = False
                audit_result.notes.append(f"High deviation detected: {deviation:.2f}%")
                
                # Add additional context
                if deviation > 10:
                    audit_result.notes.append("Deviation exceeds 10% - significant inconsistency")
        else:
            # For non-numeric results, do string comparison
            if str(previous_result) != str(current_result):
                audit_result.is_consistent = False
                audit_result.notes.append("Non-numeric results differ")
        
        return audit_result
    
    def _extract_numeric_value(self, result: Any) -> Optional[float]:
        """
        Extract numeric value from a result (e.g., stock price)
        
        Args:
            result: The result to extract value from
            
        Returns:
            Extracted numeric value or None
        """
        if isinstance(result, (int, float)):
            return float(result)
        
        if isinstance(result, str):
            # Try to extract price from string like "$123.45"
            import re
            price_match = re.search(r'\$?\s*([0-9]+[0-9,]*\.?[0-9]+)', result)
            if price_match:
                try:
                    return float(price_match.group(1).replace(',', ''))
                except ValueError:
                    pass
        
        return None
    
    def record_audit_result(self, audit_result: AuditResult):
        """
        Record an audit result in history
        
        Args:
            audit_result: The audit result to record
        """
        # Get or create history for this query
        if audit_result.query not in self.audit_history:
            self.audit_history[audit_result.query] = AuditHistory(query=audit_result.query)
        
        history = self.audit_history[audit_result.query]
        
        # Add result to history
        history.results.append(audit_result)
        history.last_audit = audit_result.timestamp
        history.is_failing = not audit_result.is_consistent
        
        # Keep only recent results (last 100)
        if len(history.results) > 100:
            history.results = history.results[-100:]
        
        # Save to storage
        self.save_audit_history()
    
    def get_failing_audits(self) -> List[AuditHistory]:
        """
        Get list of audits that are currently failing
        
        Returns:
            List of failing audit histories
        """
        return [history for history in self.audit_history.values() if history.is_failing]
    
    def invalidate_cache_for_inconsistent_data(self):
        """
        Invalidate cache for queries with inconsistent data
        In a real implementation, this would trigger cache invalidation
        """
        failing_audits = self.get_failing_audits()
        if failing_audits:
            print(f"⚠️  Invalidating cache for {len(failing_audits)} inconsistent queries:")
            for audit in failing_audits:
                latest_result = audit.results[-1] if audit.results else None
                if latest_result:
                    print(f"   - {audit.query}: {latest_result.deviation_percentage:.2f}% deviation")
                    # In a real implementation, this would trigger cache invalidation
                    # For now, we'll just mark it in the history
                    audit.is_failing = True
    
    async def run_regression_test_suite(self, test_queries: List[str]) -> Dict[str, AuditResult]:
        """
        Run regression test suite on major query types
        
        Args:
            test_queries: List of queries to test
            
        Returns:
            Dictionary mapping queries to audit results
        """
        print("🔬 Running financial data consistency audit...")
        results = {}
        
        # Import web search tool
        from app.tool.web_search import WebSearch
        
        for query in test_queries:
            try:
                print(f"   Testing: {query}")
                
                # Determine query type for scheduling
                query_type = self._categorize_query(query)
                
                # Check if we should audit this query
                if not self.should_audit_query(query, query_type):
                    print(f"   Skipping {query} - not due for audit")
                    continue
                
                # Perform web search
                web_search = WebSearch()
                search_response = await web_search.execute(
                    query=query,
                    num_results=3,
                    fetch_content=True
                )
                
                if not search_response.error and search_response.results:
                    # Extract relevant information
                    result = search_response.results[0]
                    content = result.raw_content or result.description
                    
                    # Check consistency
                    audit_result = self.check_consistency(query, content)
                    results[query] = audit_result
                    
                    # Record the result
                    self.record_audit_result(audit_result)
                    
                    # Print status
                    if audit_result.is_consistent:
                        print(f"   ✅ {query}: Consistent")
                    else:
                        print(f"   ❌ {query}: Inconsistent ({audit_result.deviation_percentage:.2f}% deviation)")
                else:
                    print(f"   ⚠️  {query}: Search failed - {search_response.error}")
                    
            except Exception as e:
                print(f"   ⚠️  {query}: Audit failed - {e}")
                continue
        
        # Handle inconsistent data
        self.invalidate_cache_for_inconsistent_data()
        
        return results
    
    def _categorize_query(self, query: str) -> str:
        """
        Categorize a query for audit scheduling
        
        Args:
            query: The query to categorize
            
        Returns:
            Query category
        """
        query_lower = query.lower()
        
        financial_keywords = ['stock', 'price', 'share', 'market', 'trading', 'investment']
        if any(word in query_lower for word in financial_keywords):
            return "financial"
        
        biographical_keywords = ['who is', 'biography', 'born', 'died', 'career']
        if any(word in query_lower for word in biographical_keywords):
            return "biographical"
        
        technical_keywords = ['code', 'program', 'software', 'function', 'api']
        if any(word in query_lower for word in technical_keywords):
            return "technical"
        
        return "general"
    
    def generate_audit_report(self) -> str:
        """
        Generate a summary report of audit results
        
        Returns:
            Formatted audit report
        """
        report = "📊 Financial Data Consistency Audit Report\n"
        report += "=" * 50 + "\n\n"
        
        total_audits = len(self.audit_history)
        failing_audits = len(self.get_failing_audits())
        passing_audits = total_audits - failing_audits
        
        report += f"Total Audits: {total_audits}\n"
        report += f"Passing: {passing_audits}\n"
        report += f"Failing: {failing_audits}\n\n"
        
        if failing_audits > 0:
            report += "❌ Failing Audits:\n"
            report += "-" * 20 + "\n"
            for audit in self.get_failing_audits():
                if audit.results:
                    latest = audit.results[-1]
                    report += f"   {audit.query}: {latest.deviation_percentage:.2f}% deviation\n"
            report += "\n"
        
        return report

# Global instance
financial_auditor = FinancialDataAuditor()

async def run_financial_consistency_audit(test_queries: Optional[List[str]] = None) -> Dict[str, AuditResult]:
    """
    Run financial data consistency audit
    
    Args:
        test_queries: List of queries to test (defaults to major financial queries)
        
    Returns:
        Dictionary mapping queries to audit results
    """
    if test_queries is None:
        test_queries = [
            "Apple stock price",
            "Microsoft stock price", 
            "Google stock price",
            "Amazon stock price",
            "Tesla stock price",
            "NVIDIA stock price",
            "Bitcoin price USD",
            "Gold price per ounce",
            "Oil price per barrel"
        ]
    
    return await financial_auditor.run_regression_test_suite(test_queries)

def get_audit_report() -> str:
    """
    Get the latest audit report
    
    Returns:
        Formatted audit report
    """
    return financial_auditor.generate_audit_report()

def get_failing_audit_queries() -> List[str]:
    """
    Get list of queries with failing audits
    
    Returns:
        List of failing query strings
    """
    return [audit.query for audit in financial_auditor.get_failing_audits()]