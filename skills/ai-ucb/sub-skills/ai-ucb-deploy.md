---
name: ai-ucb-deploy
description: Phase 7 Deployment sub-skill for the AI Use Case Builder. Packages all artifacts, generates Azure DevOps CI/CD pipeline YAML, creates repo structure, produces environment promotion checklists (Dev/QA/Prod), and generates deployment summary. Reads full state from ai-ucb-state.json. Invoke standalone or via orchestrator. Trigger when user mentions 'deploy', 'deployment', 'CI/CD', 'Azure DevOps pipeline', 'promote to QA', 'promote to production', 'release', 'handoff', or 'packaging'.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# AI Use Case Builder - Phase 7: Deployment & Handoff

You are the DevOps/Release agent. Your job is to package all artifacts, generate CI/CD pipelines, create the repository structure, and produce environment promotion checklists for the complete solution handoff.

**Key principle:** Never auto-push or auto-deploy without explicit user approval. Package everything, present the plan, and wait for confirmation at every stage.

## Access Control (Inherited)

1. **NEVER push code to any repository without user approval.** Present the plan, get explicit "yes."
2. **NEVER deploy to QA or Production automatically.** Manual approval gates are mandatory.
3. **NEVER include secrets in the repo.** Use `.env.template` files, Key Vault references, and pipeline variable groups.
4. **NEVER modify existing UBI pipelines.** Create new pipelines alongside existing ones.

## Prerequisites

- Phase 6 (Documentation) must be `completed` in `ai-ucb-state.json`
- Required state: all phases completed, all artifacts generated

## Deployment Flow

### Step 1: Read State and Verify Completeness

```python
state = read_json("ai-ucb-state.json")

# Verify all phases complete
required_phases = ["discovery", "infra", "pipeline", "ai", "frontend", "test", "docs"]
for phase in required_phases:
    assert state["phases"][phase] == "completed", f"Phase {phase} not completed"

# Gather all artifacts
artifacts = state["artifacts"]
archetype = state["archetype"]
naming = state["naming"]
```

### Step 2: Artifact Inventory

Verify all expected artifacts exist and are non-empty:

```
ARTIFACT INVENTORY
| Category | Artifact | Files | Status |
|----------|----------|-------|--------|
| Infrastructure | Bicep templates | main.bicep + modules/ | {exists} |
| Infrastructure | CLI scripts | provision.sh | {exists} |
| Pipeline | ADF pipeline JSON | PL_{app}_Master.json | {exists} |
| Pipeline | Databricks notebooks | Bronze, Silver, Gold, AI Layer | {exists} |
| Pipeline | Status control SQL | StatusControl.sql | {exists} |
| Application | Frontend code | app.py / Next.js project | {exists} |
| Application | Requirements | requirements.txt / package.json | {exists} |
| Application | Dockerfile | Dockerfile (React only) | {exists or N/A} |
| CI/CD | Infra pipeline YAML | infra-pipeline.yml | {to generate} |
| CI/CD | App pipeline YAML | app-pipeline.yml | {to generate} |
| Documentation | 8 enterprise docs | MD + DOCX | {exists} |
| State | ai-ucb-state.json | State contract | {exists} |
| State | PROJECT_MEMORY.md | Decision log | {exists} |
```

### Step 3: Repository Structure

Generate recommended directory layout:

```
{repo-name}/
├── README.md                       # Project overview (generated)
├── .gitignore                      # Azure + Python + Node patterns
├── .azuredevops/
│   ├── infra-pipeline.yml          # Infrastructure CI/CD
│   ├── app-pipeline.yml            # Application CI/CD
│   └── notebook-pipeline.yml       # Databricks notebook sync
├── infra/
│   ├── main.bicep                  # Bicep orchestrator
│   ├── modules/
│   │   ├── ai-services.bicep
│   │   ├── ai-search.bicep
│   │   ├── cosmos-db.bicep
│   │   ├── key-vault.bicep
│   │   ├── storage.bicep
│   │   ├── app-service.bicep
│   │   └── managed-identity.bicep
│   └── parameters/
│       ├── dev.parameters.json
│       ├── qa.parameters.json
│       └── prod.parameters.json
├── pipelines/
│   ├── PL_{app}_Master.json        # ADF pipeline definition
│   ├── linked-services/            # ADF linked service configs
│   └── triggers/                   # ADF trigger configs
├── notebooks/
│   ├── Bronze_{app}_{source}.py
│   ├── Silver_{app}.py
│   ├── Gold_{app}.py
│   ├── AILayer_{app}.py
│   └── Publish_AISearch_{app}.py
├── src/
│   ├── app.py                      # Streamlit app (or Next.js)
│   ├── requirements.txt
│   ├── startup.sh
│   ├── .env.template
│   └── utils/
│       ├── ai_client.py
│       ├── search_client.py
│       └── auth.py
├── tests/
│   └── test_queries.json           # AI quality test cases
├── docs/
│   ├── README.md                   # Document index
│   ├── ea-document.md
│   ├── solution-design.md
│   ├── data-flow.md
│   ├── api-spec.md
│   ├── developer-guide.md
│   ├── user-guide.md
│   ├── operations-runbook.md
│   └── stm.md
└── state/
    ├── ai-ucb-state.json
    └── PROJECT_MEMORY.md
```

### Step 4: Azure DevOps Pipeline YAML Generation

#### 4a. Infrastructure Pipeline

```yaml
# .azuredevops/infra-pipeline.yml
trigger:
  branches:
    include: [main]
  paths:
    include: [infra/*]

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: flk-{app}-infra-vars  # Variable group with subscription IDs, etc.

stages:
  - stage: Validate
    jobs:
      - job: BicepValidate
        steps:
          - task: AzureCLI@2
            displayName: 'Validate Bicep'
            inputs:
              azureSubscription: 'flk-ai-service-connection'
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                az deployment group validate \
                  --resource-group flk-$(APP_SLUG)-dev-rg \
                  --template-file infra/main.bicep \
                  --parameters infra/parameters/dev.parameters.json

  - stage: DeployDev
    dependsOn: Validate
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployInfra
        environment: 'flk-{app}-dev'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureCLI@2
                  displayName: 'Deploy Bicep to Dev'
                  inputs:
                    azureSubscription: 'flk-ai-service-connection'
                    scriptType: bash
                    scriptLocation: inlineScript
                    inlineScript: |
                      az deployment group create \
                        --resource-group flk-$(APP_SLUG)-dev-rg \
                        --template-file infra/main.bicep \
                        --parameters infra/parameters/dev.parameters.json

  - stage: DeployQA
    dependsOn: DeployDev
    condition: succeeded()
    jobs:
      - deployment: DeployInfraQA
        environment: 'flk-{app}-qa'  # Manual approval gate in Azure DevOps
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureCLI@2
                  displayName: 'Deploy Bicep to QA'
                  inputs:
                    azureSubscription: 'flk-ai-service-connection'
                    scriptType: bash
                    scriptLocation: inlineScript
                    inlineScript: |
                      az deployment group create \
                        --resource-group flk-$(APP_SLUG)-qa-rg \
                        --template-file infra/main.bicep \
                        --parameters infra/parameters/qa.parameters.json

  - stage: DeployProd
    dependsOn: DeployQA
    condition: succeeded()
    jobs:
      - deployment: DeployInfraProd
        environment: 'flk-{app}-prod'  # Manual approval + change control
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureCLI@2
                  displayName: 'What-If (Prod)'
                  inputs:
                    azureSubscription: 'flk-ai-service-connection-prod'
                    scriptType: bash
                    scriptLocation: inlineScript
                    inlineScript: |
                      az deployment group what-if \
                        --resource-group flk-$(APP_SLUG)-prod-rg \
                        --template-file infra/main.bicep \
                        --parameters infra/parameters/prod.parameters.json
                - task: AzureCLI@2
                  displayName: 'Deploy Bicep to Prod'
                  inputs:
                    azureSubscription: 'flk-ai-service-connection-prod'
                    scriptType: bash
                    scriptLocation: inlineScript
                    inlineScript: |
                      az deployment group create \
                        --resource-group flk-$(APP_SLUG)-prod-rg \
                        --template-file infra/main.bicep \
                        --parameters infra/parameters/prod.parameters.json
```

#### 4b. Application Pipeline

```yaml
# .azuredevops/app-pipeline.yml
trigger:
  branches:
    include: [main]
  paths:
    include: [src/*]

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: flk-{app}-app-vars

stages:
  - stage: Build
    jobs:
      - job: BuildApp
        steps:
          - task: UsePythonVersion@0
            inputs: { versionSpec: '3.11' }
          - script: |
              cd src && pip install -r requirements.txt
              # Run linting / type checks if configured
            displayName: 'Install and Validate'

  - stage: DeployDev
    dependsOn: Build
    jobs:
      - deployment: DeployApp
        environment: 'flk-{app}-dev'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  displayName: 'Deploy to App Service'
                  inputs:
                    azureSubscription: 'flk-ai-service-connection'
                    appType: 'webAppLinux'
                    appName: 'flk-$(APP_SLUG)-app-dev'
                    package: 'src/'
                    startUpCommand: 'startup.sh'
```

#### 4c. Notebook Deployment Pipeline (Databricks Asset Bundles)

**Use Databricks Asset Bundles (DABs)** instead of raw `workspace import_dir`. DABs provide declarative, non-destructive deployment with rollback support.

```yaml
# .azuredevops/notebook-pipeline.yml
trigger:
  branches:
    include: [main]
  paths:
    include: [notebooks/*, databricks.yml]

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: flk-$(APP_SLUG)-databricks-vars

stages:
  - stage: Validate
    jobs:
      - job: ValidateBundle
        steps:
          - task: Bash@3
            displayName: 'Install Databricks CLI v0.200+'
            inputs:
              targetType: inline
              script: |
                curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
                databricks --version
          - task: Bash@3
            displayName: 'Validate bundle'
            inputs:
              targetType: inline
              script: |
                export DATABRICKS_HOST=$(DATABRICKS_HOST)
                export DATABRICKS_TOKEN=$(DATABRICKS_TOKEN)
                databricks bundle validate --target dev

  - stage: DeployDev
    dependsOn: Validate
    jobs:
      - deployment: DeployNotebooks
        environment: 'flk-$(APP_SLUG)-databricks-dev'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: Bash@3
                  displayName: 'Deploy bundle to dev'
                  inputs:
                    targetType: inline
                    script: |
                      curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
                      export DATABRICKS_HOST=$(DATABRICKS_HOST)
                      export DATABRICKS_TOKEN=$(DATABRICKS_TOKEN)
                      # Non-destructive: only updates changed files
                      databricks bundle deploy --target dev
                - task: Bash@3
                  displayName: 'Run smoke test job'
                  inputs:
                    targetType: inline
                    script: |
                      export DATABRICKS_HOST=$(DATABRICKS_HOST)
                      export DATABRICKS_TOKEN=$(DATABRICKS_TOKEN)
                      # Trigger a validation job defined in the bundle
                      databricks bundle run smoke_test --target dev
```

**Databricks Asset Bundle configuration** (`databricks.yml`):

```yaml
# databricks.yml — Declarative bundle for notebook deployment
bundle:
  name: flk-$(APP_SLUG)-notebooks

workspace:
  host: ${DATABRICKS_HOST}

targets:
  dev:
    workspace:
      root_path: /Shared/$(APP_SLUG)/dev
    resources:
      jobs:
        smoke_test:
          name: "$(APP_SLUG)_smoke_test"
          tasks:
            - task_key: validate_bronze
              notebook_task:
                notebook_path: ./notebooks/Bronze_$(APP_SLUG)_validate.py
              new_cluster:
                spark_version: "14.3.x-scala2.12"
                node_type_id: "Standard_DS3_v2"
                num_workers: 0
  qa:
    workspace:
      root_path: /Shared/$(APP_SLUG)/qa
  prod:
    workspace:
      root_path: /Shared/$(APP_SLUG)/prod

resources:
  jobs:
    main_pipeline:
      name: "$(APP_SLUG)_pipeline"
      schedule:
        quartz_cron_expression: "0 0 6 * * ?"
        timezone_id: "America/Los_Angeles"
      tasks:
        - task_key: bronze
          notebook_task:
            notebook_path: ./notebooks/Bronze_$(APP_SLUG).py
            base_parameters:
              StreamName: $(APP_SLUG)
        - task_key: silver
          depends_on: [{task_key: bronze}]
          notebook_task:
            notebook_path: ./notebooks/Silver_$(APP_SLUG).py
        - task_key: gold
          depends_on: [{task_key: silver}]
          notebook_task:
            notebook_path: ./notebooks/Gold_$(APP_SLUG).py
        - task_key: ai_layer
          depends_on: [{task_key: gold}]
          notebook_task:
            notebook_path: ./notebooks/AILayer_$(APP_SLUG).py

include:
  - notebooks/*.py
```

**Why DABs over `import_dir --overwrite`:**
- Non-destructive: only changes modified files, never deletes unexpected files
- Declarative: bundle config is version-controlled alongside notebooks
- Job management: creates/updates Databricks jobs from YAML definition
- Rollback: `databricks bundle destroy --target dev` cleanly removes deployed artifacts
- Multi-target: same bundle deploys to dev/qa/prod with different configs

### Step 4d: Blue/Green Deployment for App Service

Use deployment slots for zero-downtime deployments with instant rollback:

```yaml
# Enhanced app-pipeline.yml with blue/green deployment
  - stage: DeployDev_BlueGreen
    dependsOn: Build
    jobs:
      - deployment: DeployToStaging
        environment: 'flk-$(APP_SLUG)-dev'
        strategy:
          runOnce:
            deploy:
              steps:
                # Step 1: Deploy to staging slot (not live traffic)
                - task: AzureWebApp@1
                  displayName: 'Deploy to staging slot'
                  inputs:
                    azureSubscription: 'flk-ai-service-connection'
                    appType: 'webAppLinux'
                    appName: 'flk-$(APP_SLUG)-app-dev'
                    deployToSlotOrASE: true
                    slotName: 'staging'
                    package: 'src/'
                    startUpCommand: 'startup.sh'

                # Step 2: Smoke test the staging slot
                - task: Bash@3
                  displayName: 'Smoke test staging slot'
                  inputs:
                    targetType: inline
                    script: |
                      echo "Testing staging slot..."
                      HEALTH=$(curl -s -o /dev/null -w "%{http_code}" \
                        https://flk-$(APP_SLUG)-app-dev-staging.azurewebsites.net/health)
                      if [ "$HEALTH" != "200" ]; then
                        echo "FAIL: Staging health check returned $HEALTH"
                        exit 1
                      fi

                      # Test chat endpoint
                      CHAT=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
                        https://flk-$(APP_SLUG)-app-dev-staging.azurewebsites.net/api/chat \
                        -H "Content-Type: application/json" \
                        -d '{"messages":[{"role":"user","content":"health check"}]}')
                      if [ "$CHAT" != "200" ]; then
                        echo "FAIL: Chat endpoint returned $CHAT"
                        exit 1
                      fi
                      echo "PASS: Staging slot healthy"

                # Step 3: Swap staging → production (instant, zero-downtime)
                - task: AzureAppServiceManage@0
                  displayName: 'Swap staging to production'
                  inputs:
                    azureSubscription: 'flk-ai-service-connection'
                    action: 'Swap Slots'
                    webAppName: 'flk-$(APP_SLUG)-app-dev'
                    resourceGroupName: 'flk-$(APP_SLUG)-dev-rg'
                    sourceSlot: 'staging'
                    targetSlot: 'production'
```

**Rollback procedure** (instant — swap back):
```bash
# If issues detected after deployment, swap back instantly
az webapp deployment slot swap \
  --name flk-${APP_SLUG}-app-${ENV} \
  --resource-group flk-${APP_SLUG}-${ENV}-rg \
  --slot staging \
  --target-slot production
echo "Rolled back to previous version (now in staging slot)"
```

### Step 4e: Model Deployment with Champion/Challenger

For Predictive ML and Computer Vision archetypes, use MLflow alias promotion:

```bash
# Current champion model serves 100% traffic
# Deploy challenger alongside for A/B testing

# Step 1: Register new model version
mlflow models register --name "${APP_SLUG}_model" --source "runs:/${RUN_ID}/model"

# Step 2: Set challenger alias on new version
python3 -c "
from mlflow.tracking import MlflowClient
client = MlflowClient()
latest = client.get_latest_versions('${APP_SLUG}_model')[0]
client.set_registered_model_alias('${APP_SLUG}_model', 'challenger', latest.version)
print(f'Challenger set to version {latest.version}')
"

# Step 3: Split traffic (90% champion, 10% challenger)
# Via Databricks Model Serving or Azure ML managed endpoint
az ml online-endpoint update \
  --name ${APP_SLUG}-endpoint \
  --workspace-name flk-${APP_SLUG}-ml-${ENV} \
  --traffic "champion=90 challenger=10"

# Step 4: After validation, promote challenger to champion
# python3 -c "client.set_registered_model_alias('${APP_SLUG}_model', 'champion', latest.version)"
# az ml online-endpoint update --traffic "champion=100"
```

### Step 5: Environment Promotion Checklists

#### Dev → QA Checklist

| # | Check | Verified | Notes |
|---|-------|---------|-------|
| 1 | All Phase 5 tests pass | | Test report artifact |
| 2 | Bicep what-if shows no unexpected changes | | Run `az deployment group what-if` |
| 3 | QA cost estimate approved | | From pricing reference |
| 4 | QA RBAC configured | | Same roles, QA resource scope |
| 5 | QA Key Vault secrets populated | | Separate keys from Dev |
| 6 | Content Safety configured in QA | | Same thresholds as Dev |
| 7 | ADF pipeline validates in QA | | Linked services point to QA |
| 8 | Smoke test passes in QA | | Run test sub-skill against QA |

#### QA → Prod Checklist

| # | Check | Verified | Notes |
|---|-------|---------|-------|
| 1 | UAT sign-off from business stakeholder | | Written approval |
| 2 | Security review completed | | Vulnerability scan, RBAC audit |
| 3 | Performance benchmarks met | | Response time < 3s, throughput > 50 req/min |
| 4 | Change control ticket approved | | ServiceNow / change management |
| 5 | Rollback plan documented | | Step-by-step rollback procedure |
| 6 | Multi-region failover tested | | Cosmos failover, Front Door routing |
| 7 | Production capacity provisioned | | Upgrade SKUs from Dev sizes |
| 8 | Monitoring and alerts configured | | Log Analytics, App Insights, alert rules |
| 9 | Documentation reviewed and approved | | All 8 docs current |
| 10 | Support escalation path defined | | On-call rotation, contacts |

### Step 6: Generate Deployment Summary

```
DEPLOYMENT SUMMARY — {project_name}
======================================

SOLUTION OVERVIEW
  Archetype: {archetype}
  Primary Model: {model} ({deployment})
  Frontend: {frontend_type} → {app_url}
  Data Sources: {source_count} ({source_list})
  Pipeline: PL_{app}_Master ({schedule})
  Monthly Cost (Dev): ~${cost_estimate}

ARTIFACT INVENTORY
  Infrastructure: {file_count} Bicep files
  Pipelines: 1 ADF + {notebook_count} notebooks
  Application: {app_file_count} source files
  CI/CD: 3 Azure DevOps pipeline YAML
  Documentation: 8 enterprise documents
  Total Files: {total_file_count}

REPOSITORY
  Repo: dev.azure.com/flukeit/Fluke Data And Analytics/_git/{repo}
  Branch: Users/{username}/{app}
  Status: {ready to push / already pushed}

CI/CD PIPELINES
  infra-pipeline.yml    → Bicep deploy (Dev auto / QA+Prod manual)
  app-pipeline.yml      → App Service deploy
  notebook-pipeline.yml → Databricks sync

ENVIRONMENT STATUS
  Dev: Deployed and tested ✓
  QA: Checklist ready (8 items)
  Prod: Checklist ready (10 items)

OPERATIONAL HANDOFF
  Operations Runbook: docs/operations-runbook.md
  Developer Guide: docs/developer-guide.md
  Key Contacts: {owner}, {team}
  Escalation: {escalation_path}

PROJECT COMPLETE — All 8 phases finished.
```

Update state: `phases.deploy = "completed"`, mark project as complete.
Update `PROJECT_MEMORY.md`: Add completion timestamp, final artifact inventory.

Ask:
> **GATE: Phase 7 Deployment complete.** All artifacts packaged, CI/CD pipelines generated, promotion checklists ready. Shall I push to Azure DevOps? (Requires explicit approval)

---

## Deployment Anti-Patterns (NEVER Do These)

1. **NEVER auto-push to Azure DevOps without user approval.** The user must explicitly say "push" or "deploy." Packaging is not deploying.
2. **NEVER commit `.env` files or `local.settings.json` with real values.** Only `.env.template` and `.template` files go in the repo.
3. **NEVER create a single pipeline for all environments.** Separate pipeline files (or at minimum, separate stages with manual gates) for Dev/QA/Prod.
4. **NEVER skip the Bicep `what-if` before Production deployment.** What-if shows what will change — deploying blind to Production is reckless.
5. **NEVER promote to Production without the 10-item checklist.** Skipping UAT, security review, or change control creates operational risk.
6. **NEVER overwrite existing UBI DevOps pipelines.** Create new pipeline files alongside existing ones. Existing streams must continue working.
7. **NEVER deploy Production with Dev-tier SKUs.** The promotion process must upgrade App Service, AI Search, Cosmos DB SKUs per the pricing reference.

## Rollback Procedures (by Layer)

| Layer | Rollback Method | Time to Rollback |
|-------|----------------|------------------|
| **App Service** | Slot swap: `az webapp deployment slot swap --slot staging` | ~5 seconds |
| **Databricks notebooks** | DABs: `databricks bundle deploy --target dev` (redeploy previous commit) | ~30 seconds |
| **AI model** | MLflow alias: set champion alias back to previous version | ~10 seconds |
| **Infrastructure** | Bicep: redeploy with previous parameter file | ~2-5 minutes |
| **AI Search index** | Rebuild from source: re-run Phase 2 AI Layer notebooks | ~10-30 minutes |
| **Cosmos DB** | Point-in-time restore: `az cosmosdb restore` (last 30 days) | ~5-15 minutes |
| **ADLS data** | Delta time travel: `RESTORE TABLE ... TO VERSION AS OF {n-1}` | ~1 minute |

**Automated rollback script:**

```bash
#!/bin/bash
# rollback.sh — Automated rollback for flk-{app} deployment
# Usage: ./rollback.sh {layer} {env}
# Layers: app, notebooks, model, infra, all

LAYER="$1"
ENV="${2:-dev}"
APP_SLUG="${3:-$(jq -r .naming.app_slug ai-ucb-state.json)}"

case "$LAYER" in
  app)
    echo "Rolling back App Service..."
    az webapp deployment slot swap \
      --name "flk-${APP_SLUG}-app-${ENV}" \
      --resource-group "flk-${APP_SLUG}-${ENV}-rg" \
      --slot staging --target-slot production
    ;;
  notebooks)
    echo "Rolling back Databricks notebooks..."
    git stash
    git checkout HEAD~1 -- notebooks/
    databricks bundle deploy --target "$ENV"
    git stash pop
    ;;
  model)
    echo "Rolling back ML model to previous champion..."
    python3 -c "
from mlflow.tracking import MlflowClient
client = MlflowClient()
# Get the version currently aliased as 'champion'
champion = client.get_model_version_by_alias('${APP_SLUG}_model', 'champion')
# Set previous version as champion (version - 1)
prev_version = str(int(champion.version) - 1)
client.set_registered_model_alias('${APP_SLUG}_model', 'champion', prev_version)
print(f'Rolled back to model version {prev_version}')
"
    ;;
  infra)
    echo "Rolling back infrastructure (Bicep redeploy)..."
    git checkout HEAD~1 -- infra/parameters/${ENV}.parameters.json
    az deployment group create \
      --resource-group "flk-${APP_SLUG}-${ENV}-rg" \
      --template-file infra/main.bicep \
      --parameters "infra/parameters/${ENV}.parameters.json"
    ;;
  all)
    echo "Rolling back ALL layers..."
    $0 app "$ENV" "$APP_SLUG"
    $0 notebooks "$ENV" "$APP_SLUG"
    $0 model "$ENV" "$APP_SLUG"
    ;;
  *)
    echo "Usage: $0 {app|notebooks|model|infra|all} {dev|qa|prod}"
    exit 1
    ;;
esac

echo "Rollback complete. Verify health: curl https://flk-${APP_SLUG}-app-${ENV}.azurewebsites.net/health"
```

## Error Recovery

| Error | Recovery |
|-------|---------|
| Azure DevOps service connection fails | Verify service principal: `az ad sp show --id {sp-id}`. Recreate if expired |
| Bicep what-if shows unexpected deletes | Review parameter files, verify resource names match. **NEVER deploy if what-if shows deletes** — investigate first |
| DABs deploy fails (401) | Verify Databricks token: `databricks auth env`. Refresh via Key Vault |
| DABs deploy fails (bundle validation) | Run `databricks bundle validate --target dev` locally to identify YAML issues |
| App Service deploy 409 Conflict | Check if slot swap is in progress: `az webapp deployment slot list`. Wait and retry |
| Staging slot smoke test fails | Do NOT swap. Check logs: `az webapp log tail --name flk-{app}-app-dev --slot staging` |
| Pipeline YAML validation error | Check indentation, verify task versions (`AzureCLI@2` not `@1`), review variable groups |
| Repo push rejected (403) | Verify Azure DevOps permissions, check branch policies. Try: `az devops login` |
| Model deployment 429 (quota) | Check TPM usage, try secondary region, or reduce capacity |
| Blue/green swap fails | Check slot status: `az webapp deployment slot show`. Force swap if stuck: `--action swap` |
