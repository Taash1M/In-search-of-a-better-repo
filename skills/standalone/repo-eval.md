---
name: repo-eval
description: Evaluate, enhance, and adopt open-source repositories. Use when reviewing repos for production readiness, security, feature completeness, and deployment suitability. Covers the full lifecycle from initial review through backup, enhancement, and integration.
license: Apache-2.0
---

# Repository Evaluation, Enhancement & Adoption

Systematic workflow for evaluating open-source repositories, identifying production concerns, implementing improvements, and preparing for organizational adoption.

## When to Use

- Evaluating a new open-source project for adoption
- Reviewing a forked repo for completeness and security
- Preparing a repo backup with documentation and deployment configs
- Enhancing an existing project with missing capabilities

## Phase 1: Initial Assessment

### 1.1 Clone and Inventory

```
git clone <repo-url> <repo-name>-review
```

Inventory all files, count by type, identify:
- Language/framework (package.json, pyproject.toml, Cargo.toml, etc.)
- Entry points (main, app, src)
- Tests (tests/, __tests__/, *.test.*, *.spec.*)
- CI/CD (.github/workflows/, .gitlab-ci.yml)
- Docker/deployment (Dockerfile, docker-compose.yml, vercel.json)
- Documentation (README.md, docs/)
- Configuration (.env.example, config/)

### 1.2 Read Core Files (in priority order)

1. README.md — claimed features, architecture, setup instructions
2. Package manifest (package.json / pyproject.toml) — dependencies, scripts
3. Main API/entry point — core logic, request handling
4. Configuration/providers — how external services connect
5. Security-relevant files — middleware, auth, env handling
6. Docker/deployment — build process, runtime config
7. Tests — coverage, patterns, fixtures

## Phase 2: Evaluation Scorecard

Rate each category 1-10 with evidence:

| Category | What to Check |
|----------|---------------|
| **Architecture** | Separation of concerns, proper patterns, scalability |
| **Code Quality** | TypeScript/types, linting, formatting, naming conventions |
| **Security** | Auth, input validation, SSRF/XSS/injection prevention, secret handling, error filtering |
| **Feature Completeness** | Does it do what README claims? Verify each feature against code |
| **Deployment Readiness** | Docker, env config, standalone builds, documented setup |
| **Testing** | Test coverage, fixtures, CI integration |
| **Documentation** | README quality, API docs, inline comments where needed |

### Security Checklist

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] No suspicious network calls (crypto miners, data exfiltration)
- [ ] Input validation at system boundaries
- [ ] Path traversal protection for file operations
- [ ] SSRF prevention for user-provided URLs
- [ ] Error messages don't leak sensitive data
- [ ] Dependencies are known, maintained packages
- [ ] Docker runs as non-root user
- [ ] No eval() or dynamic code execution with user input

### Malicious Content Scan

Search for:
- Obfuscated code (base64 decode + eval patterns)
- Unexpected network requests (fetch/axios to unknown domains)
- Cryptocurrency references (mining, wallet addresses)
- Environment variable exfiltration
- Backdoor patterns (reverse shells, unauthorized access)

## Phase 3: Production Concerns Report

Identify and categorize concerns:

**Blocking** — Must fix before deployment:
- Security vulnerabilities
- Missing authentication
- Data leaks in error responses

**Important** — Should fix for production:
- Missing tests
- Debug logging in production
- Client-only rate limiting
- Missing security headers

**Nice to have** — Improve over time:
- Type safety improvements
- Code organization refinements
- Additional documentation

## Phase 4: Enhancement Implementation

For each identified concern:

1. **Plan** — Define the approach, matching existing code patterns
2. **Implement** — Make minimal, focused changes
3. **Verify** — Ensure the fix works and doesn't break existing functionality

### Common Enhancements

| Enhancement | Pattern |
|-------------|---------|
| Add tests | Mirror existing test structure, use same framework |
| Loosen dependency pins | `==x.y.z` → `>=x.y.z,<x.(y+10).0` |
| Add file format support | Follow existing converter/adapter pattern |
| Split monolithic files | Extract shared base, keep class names for compatibility |
| Add deployment config | Dockerfile, docker-compose, env templates |
| Add documentation | HOW_TO guides in docs/ folder |

## Phase 5: Backup and Documentation

### 5.1 Create Backup Structure

```
backup-folder/
  repo/              # Full repo copy
  docs/              # HOW_TO guides
    HOW_TO_deploy_<project>.md
    HOW_TO_use_<project>.md
    HOW_TO_<specific_feature>.md
  examples/          # Usage examples for your organization
  README.md          # Project overview with rating and structure
```

### 5.2 Documentation Templates

Each HOW_TO should cover:
- Prerequisites
- Step-by-step instructions with code examples
- Configuration options
- Troubleshooting table

### 5.3 Add to Portfolio

```
git add <project-number>_<Project_Name>/
git commit -m "Add project <N>: <Name> — <brief description>"
```

## Phase 6: Deployment Preparation

### 6.1 Environment Configuration

- Create `.env.example` or `.env.template` with all required variables
- Document which variables are required vs optional
- Include provider-specific configurations

### 6.2 Docker Deployment

Verify or create:
- Multi-stage Dockerfile (deps → build → runtime)
- Non-root user in production stage
- Standalone/optimized build output
- Health check endpoint

### 6.3 Cloud Deployment

Document deployment to target platform:
- Environment variables to set
- Network/firewall requirements
- Storage/persistence needs
- Scaling considerations

## Evaluation Report Template

```markdown
## <Project Name> — Evaluation Report

**Repo:** <url>
**Version:** <version> | **License:** <license>
**Stack:** <framework, language, key deps>

### Scoring

| Category | Score | Notes |
|----------|-------|-------|
| Architecture | X/10 | ... |
| Code Quality | X/10 | ... |
| Security | X/10 | ... |
| Feature Completeness | X/10 | ... |
| Deployment Readiness | X/10 | ... |
| Testing | X/10 | ... |
| Documentation | X/10 | ... |

**Overall: X.X/10**

### Security Analysis
- No malicious content detected / Issues found: ...
- Key security measures: ...
- Gaps: ...

### Feature Validation
| Claimed | Verified | Evidence |
|---------|----------|----------|

### Production Concerns
1. [Blocking/Important/Nice] — Description
2. ...

### Recommendation
Approved/Conditional/Not recommended for [backup/deployment/adoption]
Improvements needed: ...
```

## Decision Framework

| Score | Recommendation |
|-------|---------------|
| 8.5+ | Approve for backup and deployment |
| 7.0-8.4 | Approve with enhancements (implement before deployment) |
| 5.0-6.9 | Conditional — significant work needed, evaluate ROI |
| < 5.0 | Not recommended — consider alternatives |
