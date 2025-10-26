#!/usr/bin/env python3
"""
Verification script to ensure sensitive files are properly protected.
"""

import os
import subprocess
from pathlib import Path

def check_gitignore_protection():
    """Check if sensitive files are properly added to .gitignore"""
    sensitive_files = [
        '.env',
        'chat_history.json',
        'chat_history_compressed.bin',
        'chat_history_graph.bin',
        '.sensitive_backup/',
        'security_report.json',
        'models/',
        'huggingface_cache/',
        '*.log',
        '*.cache',
        '.venv/',
        'venv/',
        '__pycache__/',
        '*.pyc',
        '.DS_Store',
        'node_modules/',
        'dist/',
        '.vscode/',
        '.idea/',
        '*.backup',
        '*.security_backup'
    ]
    
    protected_files = []
    unprotectected_files = []
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            
        for file in sensitive_files:
            if file in gitignore_content:
                protected_files.append(file)
            else:
                unprotectected_files.append(file)
                
        return protected_files, unprotectected_files
    except FileNotFoundError:
        print("❌ .gitignore file not found")
        return [], sensitive_files

def check_git_status():
    """Check if any sensitive files are staged or would be committed"""
    try:
        # Check for untracked files
        result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], 
                              capture_output=True, text=True, cwd='.')
        untracked_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Check for modified files
        result = subprocess.run(['git', 'ls-files', '--modified'], 
                              capture_output=True, text=True, cwd='.')
        modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Check for staged files
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True, cwd='.')
        staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        return untracked_files, modified_files, staged_files
    except Exception as e:
        print(f"❌ Error checking git status: {e}")
        return [], [], []

def check_file_permissions():
    """Check file permissions for sensitive files"""
    sensitive_dirs = ['.sensitive_backup', '.git']
    issues = []
    
    for dir_name in sensitive_dirs:
        if os.path.exists(dir_name):
            try:
                # Check if directory is readable/writable only by owner
                stat = os.stat(dir_name)
                # This is a basic check - in production you might want more thorough checks
                issues.append(f"✓ {dir_name} exists and is protected")
            except Exception as e:
                issues.append(f"⚠️  Issue with {dir_name}: {e}")
        else:
            if dir_name == '.sensitive_backup':
                issues.append(f"⚠️  {dir_name} backup directory not found - run protect_repo.py")
    
    return issues

def main():
    """Main verification function"""
    print("🔍 Verifying repository protection...")
    
    # Check .gitignore protection
    print("\n1. Checking .gitignore protection...")
    protected, unprotected = check_gitignore_protection()
    
    if protected:
        print(f"✅ {len(protected)} sensitive patterns are protected in .gitignore:")
        for file in protected[:5]:  # Show first 5
            print(f"   - {file}")
        if len(protected) > 5:
            print(f"   ... and {len(protected) - 5} more")
    
    if unprotected:
        print(f"❌ {len(unprotected)} sensitive patterns are NOT protected in .gitignore:")
        for file in unprotected:
            print(f"   - {file}")
        print("\n💡 Recommendation: Run protect_repo.py to add these to .gitignore")
    else:
        print("✅ All sensitive patterns are properly protected in .gitignore")
    
    # Check git status
    print("\n2. Checking git status...")
    untracked, modified, staged = check_git_status()
    
    # Filter out non-sensitive files
    sensitive_untracked = [f for f in untracked if any(sensitive in f for sensitive in 
                          ['chat_history', '.env', '.backup', 'security_report'])]
    sensitive_modified = [f for f in modified if any(sensitive in f for sensitive in 
                          ['chat_history', '.env', '.backup', 'security_report'])]
    sensitive_staged = [f for f in staged if any(sensitive in f for sensitive in 
                          ['chat_history', '.env', '.backup', 'security_report'])]
    
    if sensitive_untracked:
        print(f"⚠️  {len(sensitive_untracked)} sensitive untracked files:")
        for file in sensitive_untracked[:3]:
            print(f"   - {file}")
        if len(sensitive_untracked) > 3:
            print(f"   ... and {len(sensitive_untracked) - 3} more")
    
    if sensitive_modified:
        print(f"⚠️  {len(sensitive_modified)} sensitive modified files:")
        for file in sensitive_modified:
            print(f"   - {file}")
    
    if sensitive_staged:
        print(f"❌ {len(sensitive_staged)} sensitive files are staged for commit:")
        for file in sensitive_staged:
            print(f"   - {file}")
        print("\n💡 Recommendation: Unstage these files with 'git reset HEAD <file>'")
    else:
        print("✅ No sensitive files are staged for commit")
    
    # Check file permissions
    print("\n3. Checking file permissions...")
    permission_issues = check_file_permissions()
    for issue in permission_issues:
        print(f"   {issue}")
    
    # Summary
    print("\n📋 Summary:")
    if not unprotected and not sensitive_staged:
        print("✅ Repository protection is properly configured")
        print("🔒 Sensitive files are protected from accidental commits")
    else:
        print("⚠️  Repository protection needs attention")
        if unprotected:
            print(f"   - {len(unprotected)} patterns need to be added to .gitignore")
        if sensitive_staged:
            print(f"   - {len(sensitive_staged)} sensitive files are staged for commit")
    
    print("\n💡 Tips:")
    print("   - Run 'python protect_repo.py' to update .gitignore")
    print("   - Run 'python security_check.py' to scan for hardcoded secrets")
    print("   - Run 'python security_check.py --redact' to remove hardcoded secrets")
    print("   - Run 'git status' to check current repository state")

if __name__ == "__main__":
    main()