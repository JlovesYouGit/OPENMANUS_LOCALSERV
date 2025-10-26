#!/usr/bin/env python3
"""
Security checker for the OpenManus repository.
This script performs comprehensive security checks to identify and remediate
potential security vulnerabilities.
"""

import os
import re
import json
import hashlib
from pathlib import Path

# Patterns for sensitive information
SENSITIVE_PATTERNS = {
    'api_keys': r'["\']?(api[_-]?key|API[_-]?KEY)["\']?\s*[:=]\s*["\'][a-zA-Z0-9_\-]{10,}["\']',
    'tokens': r'["\']?(token|TOKEN|access[_-]?token)["\']?\s*[:=]\s*["\'][a-zA-Z0-9_\-]{10,}["\']',
    'passwords': r'["\']?(password|PASSWORD|pass)["\']?\s*[:=]\s*["\'][a-zA-Z0-9_\-@$!%*?&]{5,}["\']',
    'secrets': r'["\']?(secret|SECRET)["\']?\s*[:=]\s*["\'][a-zA-Z0-9_\-]{10,}["\']',
    'huggingface_tokens': r'["\']?(hf_[a-zA-Z0-9]{30,})["\']',
    'generic_keys': r'["\']?[A-Za-z0-9]{40,}["\']',  # Very long strings that might be keys
}

# File extensions to scan
SCAN_EXTENSIONS = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.txt', '.md', '.cfg', '.conf', '.config'}

def scan_file_for_sensitive_data(file_path):
    """Scan a file for sensitive data patterns"""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for pattern_name, pattern in SENSITIVE_PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                findings.append({
                    'file': str(file_path),
                    'pattern': pattern_name,
                    'line': line_number,
                    'match': match.group(),
                    'position': match.span()
                })
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return findings

def scan_directory_for_sensitive_data(root_dir):
    """Scan directory for sensitive data"""
    all_findings = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip directories that should be ignored
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
            'node_modules', '__pycache__', '.git', '.venv', 'venv', '.sensitive_backup'
        ]]
        
        for file in files:
            if any(file.endswith(ext) for ext in SCAN_EXTENSIONS):
                file_path = os.path.join(root, file)
                findings = scan_file_for_sensitive_data(file_path)
                all_findings.extend(findings)
    
    return all_findings

def create_security_report(findings):
    """Create a security report from findings"""
    report = {
        'total_findings': len(findings),
        'findings_by_type': {},
        'findings_by_file': {},
        'detailed_findings': findings
    }
    
    # Group findings by type
    for finding in findings:
        pattern_type = finding['pattern']
        if pattern_type not in report['findings_by_type']:
            report['findings_by_type'][pattern_type] = 0
        report['findings_by_type'][pattern_type] += 1
        
        # Group findings by file
        file_path = finding['file']
        if file_path not in report['findings_by_file']:
            report['findings_by_file'][file_path] = []
        report['findings_by_file'][file_path].append(finding)
    
    return report

def redact_sensitive_data(file_path, findings):
    """Redact sensitive data from a file"""
    try:
        # Create backup
        backup_path = f"{file_path}.security_backup"
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(file_path, backup_path)
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Redact sensitive data (in reverse order to maintain positions)
        redacted_content = content
        for finding in sorted(findings, key=lambda x: x['position'][0], reverse=True):
            start, end = finding['position']
            redacted_content = redacted_content[:start] + '[REDACTED]' + redacted_content[end:]
        
        # Write redacted content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(redacted_content)
            
        print(f"Redacted sensitive data in {file_path}")
        return True
    except Exception as e:
        print(f"Error redacting {file_path}: {e}")
        return False

def check_git_hooks():
    """Check if git hooks are in place to prevent sensitive data commits"""
    git_hooks_dir = Path('.git/hooks')
    if not git_hooks_dir.exists():
        print("Git hooks directory not found")
        return False
    
    # Check for pre-commit hook
    pre_commit_hook = git_hooks_dir / 'pre-commit'
    if not pre_commit_hook.exists():
        print("Pre-commit hook not found")
        return False
    
    # Check if pre-commit hook contains security checks
    try:
        with open(pre_commit_hook, 'r') as f:
            content = f.read()
            if 'security_check' in content or 'sensitive' in content:
                print("Security pre-commit hook is in place")
                return True
            else:
                print("Pre-commit hook exists but may not have security checks")
                return False
    except Exception as e:
        print(f"Error checking pre-commit hook: {e}")
        return False

def setup_pre_commit_hook():
    """Setup a pre-commit hook to prevent sensitive data commits"""
    hook_content = '''#!/bin/bash
# Pre-commit hook to prevent sensitive data from being committed

# Run security check
python security_check.py --pre-commit

if [ $? -ne 0 ]; then
    echo "Security check failed. Commit aborted."
    echo "Please remove sensitive information before committing."
    exit 1
fi

echo "Security check passed. Proceeding with commit."
exit 0
'''
    
    git_hooks_dir = Path('.git/hooks')
    if not git_hooks_dir.exists():
        git_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    pre_commit_hook = git_hooks_dir / 'pre-commit'
    try:
        with open(pre_commit_hook, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        import stat
        st = os.stat(pre_commit_hook)
        os.chmod(pre_commit_hook, st.st_mode | stat.S_IEXEC)
        
        print("Pre-commit hook installed successfully")
        return True
    except Exception as e:
        print(f"Error installing pre-commit hook: {e}")
        return False

def main():
    """Main security check function"""
    import argparse
    parser = argparse.ArgumentParser(description='Security checker for OpenManus repository')
    parser.add_argument('--pre-commit', action='store_true', help='Run as pre-commit hook')
    parser.add_argument('--redact', action='store_true', help='Automatically redact sensitive data')
    args = parser.parse_args()
    
    print("🔍 Running security check on OpenManus repository...")
    
    # Scan for sensitive data
    findings = scan_directory_for_sensitive_data('.')
    
    if findings:
        print(f"⚠️  Found {len(findings)} potential sensitive data items")
        
        # Create security report
        report = create_security_report(findings)
        
        # Save report
        with open('security_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("📝 Security report saved to security_report.json")
        
        # Display summary
        print("\n📊 Summary:")
        for pattern_type, count in report['findings_by_type'].items():
            print(f"  {pattern_type}: {count}")
        
        if args.redact:
            print("\n🔄 Redacting sensitive data...")
            # Group findings by file
            files_to_redact = {}
            for finding in findings:
                file_path = finding['file']
                if file_path not in files_to_redact:
                    files_to_redact[file_path] = []
                files_to_redact[file_path].append(finding)
            
            # Redact data in each file
            for file_path, file_findings in files_to_redact.items():
                redact_sensitive_data(file_path, file_findings)
            
            print("✅ Sensitive data redaction completed")
        
        if not args.pre_commit:
            print("\n💡 Recommendations:")
            print("  1. Review the security_report.json file for details")
            print("  2. Use --redact flag to automatically redact sensitive data")
            print("  3. Consider using environment variables for sensitive data")
            print("  4. Setup pre-commit hooks to prevent future sensitive data commits")
            if input("\n  Setup pre-commit hook? (y/N): ").lower() == 'y':
                setup_pre_commit_hook()
        
        return 1 if not args.pre_commit else 1
    else:
        print("✅ No sensitive data found")
        
        # Check git hooks
        if not args.pre_commit:
            if not check_git_hooks():
                print("\n💡 Consider setting up pre-commit hooks for ongoing security")
                if input("  Setup pre-commit hook? (y/N): ").lower() == 'y':
                    setup_pre_commit_hook()
        
        return 0 if not args.pre_commit else 0

if __name__ == "__main__":
    exit(main())