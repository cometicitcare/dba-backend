#!/usr/bin/env python3
"""
Schema validation script to check all API endpoints and their response models
"""
import os
import re
import sys
from pathlib import Path

def check_route_file(file_path):
    """Check a single route file for missing response_model declarations"""
    issues = []
    
    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find all router decorator lines
    for i, line in enumerate(lines):
        if re.match(r'@router\.(get|post|put|patch|delete)\(', line):
            # Check if this is a multi-line decorator
            decorator_lines = [line]
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('def '):
                decorator_lines.append(lines[j])
                if ')' in lines[j]:
                    break
                j += 1
            
            full_decorator = ' '.join(decorator_lines)
            
            # Check if response_model is present
            if 'response_model=' not in full_decorator:
                # Get the function name
                func_line_idx = j
                if func_line_idx < len(lines):
                    func_match = re.match(r'def\s+(\w+)\(', lines[func_line_idx])
                    if func_match:
                        func_name = func_match.group(1)
                        # Extract the HTTP method and path
                        method_match = re.match(r'@router\.(\w+)\("?([^",)]*)"?', line)
                        if method_match:
                            method = method_match.group(1).upper()
                            path = method_match.group(2) or "/"
                            issues.append({
                                'file': file_path.name,
                                'line': i + 1,
                                'method': method,
                                'path': path,
                                'function': func_name,
                                'issue': 'Missing response_model'
                            })
    
    return issues

def main():
    """Main validation function"""
    routes_dir = Path(__file__).parent / 'app' / 'api' / 'v1' / 'routes'
    
    if not routes_dir.exists():
        print(f"Error: Routes directory not found: {routes_dir}")
        return 1
    
    all_issues = []
    
    # Check all Python files in routes directory
    for route_file in routes_dir.glob('*.py'):
        if route_file.name.startswith('__'):
            continue
        
        issues = check_route_file(route_file)
        all_issues.extend(issues)
    
    # Report findings
    print("=" * 80)
    print("API ENDPOINT SCHEMA VALIDATION REPORT")
    print("=" * 80)
    print()
    
    if not all_issues:
        print("✅ All endpoints have response_model declarations!")
        return 0
    
    print(f"⚠️  Found {len(all_issues)} endpoints without response_model:\n")
    
    # Group by file
    by_file = {}
    for issue in all_issues:
        file_name = issue['file']
        if file_name not in by_file:
            by_file[file_name] = []
        by_file[file_name].append(issue)
    
    for file_name, issues in sorted(by_file.items()):
        print(f"\n📄 {file_name}")
        print("-" * 80)
        for issue in issues:
            print(f"  Line {issue['line']:4d} | {issue['method']:6s} {issue['path']:30s} | {issue['function']}()")
    
    print("\n" + "=" * 80)
    print(f"Total issues: {len(all_issues)}")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
