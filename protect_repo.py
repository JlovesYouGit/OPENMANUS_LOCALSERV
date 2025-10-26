#!/usr/bin/env python3
"""
Script to protect sensitive files in the repository and remove sensitive information.
This script will:
1. Identify files that may contain sensitive information
2. Add them to .gitignore if not already present
3. Remove any hardcoded sensitive information
4. Create a backup of sensitive files
"""

import os
import re
import shutil
import hashlib
from pathlib import Path

def find_sensitive_files(root_dir):
    """Find files that may contain sensitive information"""
    sensitive_patterns = [
        r'.*\.env$',
        r'.*config.*\.json$',
        r'.*credentials.*',
        r'.*secrets.*',
        r'.*token.*',
        r'.*key.*',
        r'.*password.*',
        r'.*\.pem$',
        r'.*\.key$',
        r'.*\.crt$',
        r'.*chat_history.*',
        r'.*\.log$',
        r'.*\.cache$',
    ]
    
    sensitive_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip directories that are already ignored
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)
            
            # Check if file matches sensitive patterns
            for pattern in sensitive_patterns:
                if re.match(pattern, relative_path, re.IGNORECASE):
                    sensitive_files.append(relative_path)
                    break
                    
    return sensitive_files

def update_gitignore(root_dir, sensitive_files):
    """Update .gitignore to protect sensitive files"""
    gitignore_path = os.path.join(root_dir, '.gitignore')
    
    # Read existing .gitignore content
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    else:
        existing_content = ""
    
    # Add sensitive files to .gitignore if not already present
    additions = []
    for file in sensitive_files:
        if file not in existing_content:
            additions.append(file)
    
    if additions:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write('\n### Sensitive Files Protection ###\n')
            for file in additions:
                f.write(f'{file}\n')
        print(f"Added {len(additions)} sensitive files to .gitignore")
    else:
        print("No new sensitive files to add to .gitignore")

def remove_hardcoded_secrets(root_dir):
    """Remove hardcoded secrets from files"""
    # Common patterns for sensitive information
    secret_patterns = [
        (r'(["\']?(HF_|HUGGINGFACE_|TOKEN|SECRET|KEY|PASSWORD)["\']?\s*[:=]\s*["\'][A-Za-z0-9_\-]{10,}["\'])', '[REDACTED]'),
        (r'(hf_[a-zA-Z0-9]{30,})', '[HF_TOKEN_REDACTED]'),
        (r'(["\']?[sk]-[a-zA-Z0-9]{20,}["\']?)', '[API_KEY_REDACTED]'),
        (r'(["\']?[A-Za-z0-9]{40,}["\']?)', '[POTENTIAL_SECRET_REDACTED]'),
    ]
    
    # Files to scan for hardcoded secrets
    file_extensions = ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.txt', '.md']
    
    modified_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip directories that should be ignored
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
        
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    original_content = content
                    for pattern, replacement in secret_patterns:
                        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    
                    if content != original_content:
                        # Create backup
                        backup_path = file_path + '.backup'
                        shutil.copy2(file_path, backup_path)
                        
                        # Write cleaned content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        modified_files.append(file_path)
                        print(f"Cleaned sensitive information from: {file_path}")
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    if modified_files:
        print(f"Cleaned sensitive information from {len(modified_files)} files")
    else:
        print("No hardcoded sensitive information found")

def create_sensitive_backup(root_dir):
    """Create a backup of sensitive files in a secure location"""
    sensitive_backup_dir = os.path.join(root_dir, '.sensitive_backup')
    if not os.path.exists(sensitive_backup_dir):
        os.makedirs(sensitive_backup_dir)
    
    # Files to backup (these should already be in .gitignore)
    backup_patterns = [
        r'.*\.env$',
        r'.*chat_history.*',
        r'.*\.log$',
    ]
    
    backed_up_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip directories that should be ignored
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.sensitive_backup']]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)
            
            # Check if file matches backup patterns
            for pattern in backup_patterns:
                if re.match(pattern, relative_path, re.IGNORECASE):
                    # Create directory structure in backup
                    backup_file_path = os.path.join(sensitive_backup_dir, relative_path)
                    backup_dir = os.path.dirname(backup_file_path)
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                    
                    # Copy file to backup location
                    shutil.copy2(file_path, backup_file_path)
                    backed_up_files.append(relative_path)
                    break
    
    if backed_up_files:
        print(f"Backed up {len(backed_up_files)} sensitive files to {sensitive_backup_dir}")
        # Also add the backup directory to .gitignore
        gitignore_path = os.path.join(root_dir, '.gitignore')
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write('\n# Sensitive backup directory\n.sensitive_backup/\n')
    else:
        print("No sensitive files to backup")

def main():
    """Main function to protect the repository"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Protecting repository at: {root_dir}")
    
    # 1. Find sensitive files
    print("\n1. Finding sensitive files...")
    sensitive_files = find_sensitive_files(root_dir)
    print(f"Found {len(sensitive_files)} potentially sensitive files")
    
    # 2. Update .gitignore
    print("\n2. Updating .gitignore...")
    update_gitignore(root_dir, sensitive_files)
    
    # 3. Remove hardcoded secrets
    print("\n3. Removing hardcoded secrets...")
    remove_hardcoded_secrets(root_dir)
    
    # 4. Create backup of sensitive files
    print("\n4. Creating backup of sensitive files...")
    create_sensitive_backup(root_dir)
    
    print("\nRepository protection completed!")
    print("\nImportant notes:")
    print("- Sensitive files have been added to .gitignore")
    print("- Hardcoded secrets have been removed and files backed up")
    print("- A backup of sensitive files has been created in .sensitive_backup/")
    print("- Please verify that no sensitive information remains in your repository")
    print("- Consider using environment variables or secure secret management for sensitive data")

if __name__ == "__main__":
    main()