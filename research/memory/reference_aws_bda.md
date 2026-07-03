---
name: aws-bda-config
description: "AWS Bedrock Data Automation custom configuration for PLM engineering document extraction — 3 blueprints, project config, optimization pipeline, region us-east-2"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d0518511-12b3-40f2-a588-f406002e059b
---

## AWS BDA Custom Configuration

**Project**: `flk-ai-plmproject-techvalidation` (ARN: `arn:aws:bedrock:us-east-2:161643475055:data-automation-project/72a21e628fc6`)
**Console URL**: `https://us-east-2.console.aws.amazon.com/bedrock/home?region=us-east-2#/bda/project/details/72a21e628fc6`
**Account**: `161643475055`, <ORG_PARENT> SSO (`<USER>@<ORG_DOMAIN>`), role `SSODelegated_AdministratorAccess`
**Stage**: LIVE, ASYNC, created 2026-06-19, optimized 2026-06-19
**SSO Region**: us-east-1 (Identity Center), resources in us-east-2
**Profile ARN**: `arn:aws:bedrock:us-east-2:161643475055:data-automation-profile/us.data-automation-v1` (required for runtime invocations)
**S3 Bucket**: `flk-plm-drawings-ai-techval` (us-east-2, tagged <ORG_ABBR>-PLM-Drawings-AI)

### Blueprints (3)

| Blueprint | Class | Leaf Fields | Cost/Page |
|---|---|---|---|
| `<ORG>-component-spec` | <ORG> Component Specification | 41 | $0.0455 |
| `<ORG>-engineering-drawing` | <ORG> Engineering Drawing | 34 | $0.0420 |
| `<ORG>-product-datasheet` | Vendor Product Datasheet | 31 | $0.0405 |

All validated against AWS limits (100 leaf fields max, 30 definitions max, 100K char schema max).

### Files

**Location**: `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\AWS\blueprints\`
- `<ORG>-component-spec.json` — component spec blueprint (6 definitions, 25 top-level properties)
- `<ORG>-engineering-drawing.json` — engineering drawing blueprint (6 definitions, 20 top-level properties)
- `<ORG>-product-datasheet.json` — vendor datasheet blueprint (4 definitions, 14 top-level properties)
- `deploy_bda_project.py` — creates/updates blueprints + project, validates limits, runs test invocations
- `optimize_blueprint.py` — converts hybrid Claude extraction results to BDA ground truth format
- `ground_truth/` — 8 ground truth JSON files for blueprint optimization

### Project Configuration

- Standard output: DOCUMENT+PAGE+ELEMENT granularity, bounding boxes, generative fields, MARKDOWN+CSV, figure crops
- Custom output: 3 blueprints with auto-classification
- Override: document splitter enabled, JPEG/PNG routed as documents
- Requires `boto3` (installed on <USER> Python 3.12, v1.43.33)
- **Blueprint optimization**: 6 samples, confidence 63.2%→64.5%, DRAWING_NUMBER 0/6→4/6, invocation `cac150ab-aa6d-4da5-8ff8-492dc4f8d0c3`
- **Comparison**: BDA 4 wins, Hybrid 5 wins, 24 ties (component 2465582)

### 3-Way Comparison Results (Component 2465582)

Compared AWS BDA standard output vs our Claude hybrid extraction vs Neo4j graph:
- **AWS BDA**: excellent document structure detection (69 elements typed), figure export (PNGs), but no semantic interpretation — raw fragments that need reassembly
- **Our Hybrid**: domain-aware structured JSON with enriched values (±10% not just 10), standard-to-application linking, confidence scores. 73/80 vs BDA 16/80
- **Neo4j Graph**: only envelope properties loaded — no dimensions, standards, materials as relationship nodes (gap to close)

### AWS Resource Group (2026-06-19)

**Group**: `<ORG_ABBR>-PLM-Drawings-AI` (ARN: `arn:aws:resource-groups:us-east-2:161643475055:group/<ORG_ABBR>-PLM-Drawings-AI`)
**Tags**: Project=<ORG_ABBR>-PLM-Drawings-AI, Owner=PLM-Engineering, Environment=Technical-Validation, CostCenter=<ORG>-IT

6 resources in group:
| Resource | Type | ID |
|---|---|---|
| plm-claude-opus-4-6 | Application Inference Profile | `h5guati4rgdx` |
| plm-claude-sonnet-4-6 | Application Inference Profile | `22u8j6w2pncb` |
| plm-claude-haiku-4-5 | Application Inference Profile | `4gzyegl9cbp3` |
| plm-claude-opus-4-8 | Application Inference Profile | `9mvlo9l4xc37` |
| flk-plm-drawings-ai-techval | S3 Bucket | us-east-2 |
| <ORG_ABBR>-PLM-Drawings-AI | Resource Group | us-east-2 |

All inference profiles tested and ACTIVE. Sonnet 4.6: 1.2s latency, Opus 4.6: 1.6s latency.

### Claude Code Bedrock Configuration (2026-06-19) — ACTIVE & VERIFIED

**Active settings**: `<ADMIN_HOME>/.claude\settings.json` (Claude Code admin shell reads this, NOT <USER>'s)
**Backup (with hooks)**: `<ADMIN_HOME>/.claude\settings.azure-foundry.json.bak`
**Desktop user copy**: `<USER_HOME>/.claude\settings.json` (also Bedrock)
**Standalone Bedrock template**: `<USER_HOME>/.claude\settings.bedrock.json`

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "us-east-2",
    "AWS_PROFILE": "default"
  },
  "model": "us.anthropic.claude-opus-4-7[1m]"
}
```

**Verified via `/status`** (2026-06-19): API provider=Amazon Bedrock, region=us-east-2, model=us.anthropic.claude-opus-4-7[1m]
**Auth**: AWS SSO via `aws sso login --profile default` (<ORG_PARENT> SSO, `<ORG_PARENT>-aws.awsapps.com/start`)
**AWS config**: `<USER_HOME>/.aws\config` + `<ADMIN_HOME>/.aws\config` (both identical)
**Switch back to Azure**: `cp ~/.claude/settings.azure-foundry.json.bak ~/.claude/settings.json` + restore Windows env vars
**Swap procedure**: `<USER_HOME>/.claude\Swap\credentials_swap_azure_to_bedrock.md`
**Gotcha**: Windows User-level `ANTHROPIC_FOUNDRY_API_KEY` overrode settings.json — see [[claude-code-env-override]]

### Key Design Decisions

- 3-blueprint strategy (one per document class) for accurate auto-classification
- `inferred` type for semantic fields (drawing type, standard context, confidence)
- Dual-unit dimensions (metric + imperial as separate fields)
- Section-numbered electrical requirements matching <ORG>'s standard structure
- Blueprint optimization pipeline uses our existing hybrid Claude results as ground truth

### Cost Estimate

- Capacitor spec (4 pages): ~$0.17
- Full corpus (820 drawings x 4 avg pages): ~$420
- Blueprint optimization (10 samples): ~$4 one-time

### Deliverables

- `<USER_HOME>/Claude\deliverebles\BDA_vs_Hybrid_Extraction_Comparison.docx` — 47 KB, 5 sections (mixed landscape/portrait), 14 tables, sections A-K, cost analysis for 50 FGs, two-pass pipeline recommendation
- `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\PLM-AI-Drawing-tool-AWS\build_comparison_docx.py` — DOCX generator script
- `results/comparison_3way.json` — structured comparison data

### Related

- [[plm-drawing-extraction-validation]] — main PLM extraction project
- [[plm-drawing-agent-app]] — agent app using Neo4j graph
