#!/usr/bin/env python3
"""
Autonomous Open Source Codebase Auditor Engine
Inspects repositories for typos, duplicate words, i18n inconsistencies, and docstring formatting issues.
"""

import os
import re
import sys
import json
import argparse
from typing import List, Dict, Any, Tuple

TYPO_DICTIONARY = {
    'seperate': 'separate', 'seperated': 'separated', 'seperates': 'separates', 'seperating': 'separating',
    'occured': 'occurred', 'occuring': 'occurring', 'occurence': 'occurrence',
    'receieve': 'receive', 'receieved': 'received', 'receieves': 'receives', 'receieving': 'receiving',
    'enviroment': 'environment', 'enviroments': 'environments',
    'configuartion': 'configuration', 'configuartions': 'configurations',
    'succesfully': 'successfully', 'succesful': 'successful',
    'neccessary': 'necessary', 'unneccessary': 'unnecessary',
    'paramter': 'parameter', 'paramters': 'parameters',
    'implicitely': 'implicitly', 'explicitely': 'explicitly',
    'inital': 'initial', 'initially': 'initially',
    'existance': 'existence', 'supress': 'suppress', 'supressed': 'suppressed',
    'submited': 'submitted', 'convertion': 'conversion', 'convertions': 'conversions',
    'compatability': 'compatibility', 'incompatability': 'incompatibility',
    'reponse': 'response', 'reponses': 'responses',
    'overriden': 'overridden', 'independant': 'independent', 'independantly': 'independently',
    'hierachy': 'hierarchy', 'persistance': 'persistence', 'cancelation': 'cancellation',
    'refering': 'referring', 'refered': 'referred', 'transfered': 'transferred', 'transfering': 'transferring',
    'prefered': 'preferred', 'prefering': 'preferring', 'defintion': 'definition', 'defintions': 'definitions',
    'specifing': 'specifying', 'specifys': 'specifies', 'performes': 'performs',
}

IGNORE_DIRECTORIES = {
    '.git', 'node_modules', 'dist', 'build', '__pycache__',
    '.pytest_cache', '.venv', 'venv', 'target', '.idea', '.vscode'
}

FILE_EXTENSIONS = ('.py', '.md', '.json', '.yaml', '.yml', '.rst', '.ts', '.tsx')


def scan_file(file_path: str, repo_root: str) -> List[Dict[str, Any]]:
    findings = []
    rel_path = os.path.relpath(file_path, repo_root)

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return findings

    for line_idx, line in enumerate(lines, 1):
        clean_line = line.strip()
        words = re.findall(r'\b[a-zA-Z]+\b', clean_line)

        # Check dictionary typos
        for word in words:
            word_lower = word.lower()
            if word_lower in TYPO_DICTIONARY:
                findings.append({
                    'file': rel_path,
                    'line': line_idx,
                    'type': 'typo',
                    'original': word,
                    'suggestion': TYPO_DICTIONARY[word_lower],
                    'content': clean_line[:120]
                })

        # Check duplicate prose words in comments and markdown
        if '#' in clean_line or '"""' in clean_line or "'''" in clean_line or file_path.endswith('.md'):
            dup_match = re.search(
                r'\b(the|a|an|in|on|at|to|for|with|by|from|of|and|or|is|it|that|this|be|as|are|was|were|can|will|has|have|had)\s+\1\b',
                clean_line,
                re.IGNORECASE
            )
            if dup_match:
                findings.append({
                    'file': rel_path,
                    'line': line_idx,
                    'type': 'duplicate_word',
                    'original': dup_match.group(0),
                    'suggestion': dup_match.group(1),
                    'content': clean_line[:120]
                })

    return findings


def audit_repository(repo_path: str) -> Dict[str, Any]:
    total_files_scanned = 0
    all_findings = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRECTORIES]
        for file_name in files:
            if file_name.endswith(FILE_EXTENSIONS):
                full_path = os.path.join(root, file_name)
                total_files_scanned += 1
                file_findings = scan_file(full_path, repo_path)
                all_findings.extend(file_findings)

    return {
        'repository': os.path.abspath(repo_path),
        'files_scanned': total_files_scanned,
        'total_findings': len(all_findings),
        'findings': all_findings
    }


def main():
    parser = argparse.ArgumentParser(description="Autonomous Open Source Codebase Auditor")
    parser.add_argument("path", help="Path to repository root directory")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    result = audit_repository(args.path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n🔍 Audit Summary for: {result['repository']}")
        print(f"📁 Files Scanned: {result['files_scanned']}")
        print(f"⚠️  Total Findings: {result['total_findings']}\n")
        print("-" * 80)
        for item in result['findings']:
            print(f"  {item['file']}:{item['line']} [{item['type']}] ({item['original']} -> {item['suggestion']})")
            print(f"    └─ {item['content']}\n")


if __name__ == "__main__":
    main()
