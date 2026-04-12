#!/usr/bin/env python3
"""
Secret Scanner Hook
Detects hardcoded secrets before git commits.
Adapted for Fluke UBI / Azure environment.
"""

import json
import sys
import re
import subprocess
import os

# Secret detection patterns with descriptions
SECRET_PATTERNS = [
    # AWS Keys
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID', 'high'),
    (r'(?i)aws[_\-\s]*secret[_\-\s]*access[_\-\s]*key[\'"\s]*[=:][\'"\s]*[A-Za-z0-9/+=]{40}', 'AWS Secret Access Key', 'high'),

    # Anthropic (Claude) API Keys
    (r'sk-ant-api\d{2}-[A-Za-z0-9\-_]{20,}', 'Anthropic API Key', 'high'),

    # OpenAI API Keys
    (r'sk-[a-zA-Z0-9]{48,}', 'OpenAI API Key', 'high'),
    (r'sk-proj-[a-zA-Z0-9\-_]{32,}', 'OpenAI Project API Key', 'high'),

    # Google API Keys & Service Accounts
    (r'AIza[0-9A-Za-z\-_]{35}', 'Google API Key', 'high'),
    (r'ya29\.[0-9A-Za-z\-_]+', 'Google OAuth Access Token', 'high'),

    # Stripe API Keys
    (r'sk_live_[0-9a-zA-Z]{24,}', 'Stripe Live Secret Key', 'critical'),
    (r'sk_test_[0-9a-zA-Z]{24,}', 'Stripe Test Secret Key', 'medium'),

    # GitHub Tokens
    (r'ghp_[0-9a-zA-Z]{36}', 'GitHub Personal Access Token', 'high'),
    (r'gho_[0-9a-zA-Z]{36}', 'GitHub OAuth Token', 'high'),
    (r'ghs_[0-9a-zA-Z]{36}', 'GitHub App Secret', 'high'),
    (r'ghr_[0-9a-zA-Z]{36}', 'GitHub Refresh Token', 'high'),
    (r'github_pat_[0-9a-zA-Z_]{22,}', 'GitHub Fine-Grained PAT', 'high'),

    # GitLab Tokens
    (r'glpat-[0-9a-zA-Z\-_]{20,}', 'GitLab Personal Access Token', 'high'),

    # Databricks Personal Access Tokens
    (r'dapi[0-9a-f]{32}', 'Databricks Access Token', 'high'),

    # Azure Keys (broad pattern)
    (r'(?i)azure[_\-\s]*(?:key|secret|token)[\'"\s]*[=:][\'"\s]*[A-Za-z0-9+/=]{32,}', 'Azure Key', 'high'),

    # Azure Foundry / AI Services Keys (specific to our deployment)
    (r'(?i)(ANTHROPIC_FOUNDRY_API_KEY|AZURE_AI_KEY|COGNITIVE_SERVICE_KEY)[\'"\s]*[=:][\'"\s]*[A-Za-z0-9+/=]{32,}', 'Azure AI Service Key', 'critical'),

    # Azure Storage Account Keys
    (r'DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{44,};', 'Azure Storage Connection String', 'critical'),

    # Azure SQL / SQL Server Connection Strings
    (r'(?i)Server=[^;]+;Database=[^;]+;User Id=[^;]+;Password=[^;]+', 'SQL Server Connection String', 'high'),
    (r'(?i)Data Source=[^;]+;Initial Catalog=[^;]+;.*Password=[^;]+', 'SQL Server Connection String (alt)', 'high'),

    # Hugging Face Tokens
    (r'hf_[a-zA-Z0-9]{34,}', 'Hugging Face Token', 'high'),

    # npm / PyPI Tokens
    (r'npm_[0-9a-zA-Z]{36,}', 'npm Access Token', 'high'),
    (r'pypi-[A-Za-z0-9\-_]{16,}', 'PyPI API Token', 'high'),

    # Generic API Keys
    (r'(?i)(api[_\-\s]*key|apikey)[\'"\s]*[=:][\'"\s]*[\'"][0-9a-zA-Z\-_]{20,}[\'"]', 'Generic API Key', 'medium'),
    (r'(?i)(secret[_\-\s]*key|secretkey)[\'"\s]*[=:][\'"\s]*[\'"][0-9a-zA-Z\-_]{20,}[\'"]', 'Generic Secret Key', 'medium'),
    (r'(?i)(access[_\-\s]*token|accesstoken)[\'"\s]*[=:][\'"\s]*[\'"][0-9a-zA-Z\-_]{20,}[\'"]', 'Generic Access Token', 'medium'),

    # Passwords
    (r'(?i)password[\'"\s]*[=:][\'"\s]*[\'"][^\'"\s]{8,}[\'"]', 'Hardcoded Password', 'high'),
    (r'(?i)passwd[\'"\s]*[=:][\'"\s]*[\'"][^\'"\s]{8,}[\'"]', 'Hardcoded Password', 'high'),

    # Private Keys
    (r'-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----', 'Private Key', 'critical'),
    (r'-----BEGIN OPENSSH PRIVATE KEY-----', 'OpenSSH Private Key', 'critical'),

    # Database Connection Strings
    (r'(?i)(mysql|postgresql|postgres|mongodb)://[^\s\'"\)]+:[^\s\'"\)]+@', 'Database Connection String', 'high'),

    # JWT Tokens
    (r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', 'JWT Token', 'medium'),

    # Slack Tokens
    (r'xox[baprs]-[0-9a-zA-Z\-]{10,}', 'Slack Token', 'high'),

    # SendGrid API Keys
    (r'SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}', 'SendGrid API Key', 'high'),
]

# Files to exclude from scanning
EXCLUDED_FILES = [
    '.env.example',
    '.env.sample',
    '.env.template',
    'package-lock.json',
    'yarn.lock',
    'poetry.lock',
    'Pipfile.lock',
    'Cargo.lock',
    'go.sum',
    '.gitignore',
]

# Directories to exclude
EXCLUDED_DIRS = [
    'node_modules/',
    'vendor/',
    '.git/',
    'dist/',
    'build/',
    '__pycache__/',
    '.pytest_cache/',
    'venv/',
    'env/',
    # Private sync repo — secrets authorized by owner (private GitHub repo)
    'In search of a more perfect repo/',
]

def should_skip_file(file_path):
    """Check if file should be skipped"""
    if not os.path.exists(file_path):
        return True
    filename = os.path.basename(file_path)
    if filename in EXCLUDED_FILES:
        return True
    for excluded_dir in EXCLUDED_DIRS:
        if excluded_dir in file_path:
            return True
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return True
    except:
        return True
    return False

def get_staged_files():
    """Get list of staged files"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []

def scan_file(file_path):
    """Scan a single file for secrets"""
    findings = []
    if should_skip_file(file_path):
        return findings
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern, description, severity in SECRET_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    line_stripped = line.strip()
                    if line_stripped.startswith('#') or line_stripped.startswith('//'):
                        if 'example' in line_stripped.lower() or 'placeholder' in line_stripped.lower():
                            continue
                    findings.append({
                        'file': file_path,
                        'line': line_num,
                        'description': description,
                        'severity': severity,
                        'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                        'full_line': line.strip()[:100]
                    })
    except Exception:
        pass
    return findings

def print_findings(findings):
    """Print findings in a formatted way"""
    if not findings:
        return
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    findings.sort(key=lambda x: (severity_order.get(x['severity'], 4), x['file'], x['line']))

    print('', file=sys.stderr)
    print('SECRET SCANNER: Potential secrets detected!', file=sys.stderr)
    print('', file=sys.stderr)

    critical_count = sum(1 for f in findings if f['severity'] == 'critical')
    high_count = sum(1 for f in findings if f['severity'] == 'high')
    medium_count = sum(1 for f in findings if f['severity'] == 'medium')

    print(f'Found {len(findings)} potential secret(s):', file=sys.stderr)
    if critical_count > 0:
        print(f'  Critical: {critical_count}', file=sys.stderr)
    if high_count > 0:
        print(f'  High: {high_count}', file=sys.stderr)
    if medium_count > 0:
        print(f'  Medium: {medium_count}', file=sys.stderr)
    print('', file=sys.stderr)

    for finding in findings:
        severity_label = finding['severity'].upper()
        print(f'[{severity_label}] {finding["description"]}', file=sys.stderr)
        print(f'   File: {finding["file"]}:{finding["line"]}', file=sys.stderr)
        print(f'   Match: {finding["match"]}', file=sys.stderr)
        print('', file=sys.stderr)

    print('COMMIT BLOCKED: Remove secrets before committing', file=sys.stderr)
    print('', file=sys.stderr)
    print('How to fix:', file=sys.stderr)
    print('  1. Use environment variables or Azure Key Vault', file=sys.stderr)
    print('  2. Use Databricks secrets: dbutils.secrets.get(scope, key)', file=sys.stderr)
    print('  3. For false positives: add "example" or "placeholder" in a comment on the same line', file=sys.stderr)
    print('', file=sys.stderr)

def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = input_data.get('tool_input', {})
    command = tool_input.get('command', '')
    if not re.search(r'git\s+commit', command):
        sys.exit(0)

    # Skip scanning for explicitly authorized private repos
    AUTHORIZED_PRIVATE_REPOS = [
        'In-search-of-a-better-repo',
        'In search of a more perfect repo',
    ]
    try:
        repo_root = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True
        ).stdout.strip()
        if any(name in repo_root for name in AUTHORIZED_PRIVATE_REPOS):
            sys.exit(0)
    except Exception:
        pass

    staged_files = get_staged_files()

    if not staged_files:
        commit_match = re.search(r'git\s+commit\s+(.+)', command)
        if commit_match and re.search(r'-\w*a', commit_match.group(1)):
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True, text=True
            )
            for f in result.stdout.strip().split('\n'):
                if f.strip() and os.path.isfile(f.strip()):
                    staged_files.append(f.strip())

        for part in re.split(r'&&|;', command):
            part = part.strip()
            add_match = re.match(r'git\s+add\s+(.+)', part)
            if add_match:
                args = add_match.group(1).strip()
                if args in ('.', '-A', '--all'):
                    result = subprocess.run(
                        ['git', 'status', '--porcelain'],
                        capture_output=True, text=True
                    )
                    for line in result.stdout.strip().split('\n'):
                        if line and len(line) > 3:
                            f = line[3:].strip()
                            if os.path.isfile(f):
                                staged_files.append(f)
                else:
                    for token in args.split():
                        if not token.startswith('-') and os.path.isfile(token):
                            staged_files.append(token)

    if not staged_files:
        sys.exit(0)

    all_findings = []
    for file_path in staged_files:
        findings = scan_file(file_path)
        all_findings.extend(findings)

    if all_findings:
        print_findings(all_findings)
        sys.exit(2)

    sys.exit(0)

if __name__ == '__main__':
    main()
