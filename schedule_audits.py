#!/usr/bin/env python3
"""
Script to schedule automated consistency audits
"""

import asyncio
import time
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.consistency_audit import run_financial_consistency_audit, get_audit_report

async def run_audit_scheduler(interval_minutes: int = 60):
    """
    Run audits on a schedule
    
    Args:
        interval_minutes: Interval between audits in minutes
    """
    print(f"⏰ Audit scheduler started - running every {interval_minutes} minutes")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Running scheduled audit...")
            
            # Run the audit
            audit_results = await run_financial_consistency_audit()
            
            # Print summary
            if audit_results:
                failing_count = sum(1 for result in audit_results.values() if not result.is_consistent)
                if failing_count > 0:
                    print(f"⚠️  Found {failing_count} inconsistent results")
                else:
                    print("✅ All audits passed")
            else:
                print("ℹ️  No audits were run")
            
            # Wait for next interval
            print(f"⏳ Waiting {interval_minutes} minutes for next audit...")
            time.sleep(interval_minutes * 60)
            
    except KeyboardInterrupt:
        print("\n🛑 Audit scheduler stopped")

if __name__ == "__main__":
    # Default to hourly audits
    interval = 60
    
    # Check for command line argument
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print("Invalid interval. Using default 60 minutes.")
    
    asyncio.run(run_audit_scheduler(interval))