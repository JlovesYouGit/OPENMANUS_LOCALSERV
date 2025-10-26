#!/usr/bin/env python3
"""
Script to run automated consistency audits for financial data
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.consistency_audit import run_financial_consistency_audit, get_audit_report

async def main():
    """Run the financial consistency audit"""
    print("🚀 Starting Financial Data Consistency Audit...")
    
    # Run the audit
    audit_results = await run_financial_consistency_audit()
    
    # Print the report
    print("\n" + get_audit_report())
    
    # Check if there are any failing audits
    if audit_results:
        failing_count = sum(1 for result in audit_results.values() if not result.is_consistent)
        if failing_count > 0:
            print(f"⚠️  Found {failing_count} inconsistent results")
            print("Please review the audit results above.")
        else:
            print("✅ All audits passed - data is consistent")
    else:
        print("ℹ️  No audits were run")

if __name__ == "__main__":
    asyncio.run(main())