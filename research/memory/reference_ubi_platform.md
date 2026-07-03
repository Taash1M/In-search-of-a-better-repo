---
name: ubi-platform-key-facts
description: "UBI platform core facts — repos (AzureDataBricks/ADF/PBI), deliverables/backup folders, ubi-dev skill, STM format, Landing=Bronze, BigQuery GCP project + Key Vault secret"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

# UBI Platform — Key Facts

- **Repos**: AzureDataBricks (`<USER_HOME>/AzureDataBricks`), ADF (`<USER_HOME>/ADF`), Power BI UBI Curated Datasets
- **Deliverables folder**: `<USER_HOME>/Claude\deliverebles\`
- **Backup folder**: `<USER_HOME>/OneDrive - <ORG>\Claude code\`
- **Skill file**: `<ADMIN_HOME>/.claude\commands\ubi-dev.md`
- **STM format**: 45 columns, 7 stages (Source, Landing, Bronze, Silver, Gold DB, Gold ADLS, PBI)
- Landing = Bronze in UBI architecture (no separate raw zone)
- **BigQuery GCP project**: `cobalt-cider-279717`, service account key in Key Vault `flkubi-kv-prd` (secret: `Google-<ORG>-ServiceAccount-Json`)

Related: [[ubi-medallion-patterns]] · [[so-backlog-stream-specifics]] · [[reference-bigquery-gcp]]
