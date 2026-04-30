---
name: BigQuery / GCP Access (cobalt-cider-279717)
description: Google BigQuery project credentials, service account, Gmail login, Key Vault location — for GA/Search Console data ingestion into UBI
type: reference
originSessionId: dfe89d08-5370-4725-a763-d79180316df0
---
## GCP Project
- **Project Name**: FLK Marketing Analytics API
- **Project ID**: `cobalt-cider-279717`
- **Project Number**: `360791024370`
- **Purpose**: Ingest Google Analytics (UA + GA4) and Search Console data into Azure/Databricks for UBI

## Authentication — Service Account
- **Email**: `marketing-analytics-reporting@cobalt-cider-279717.iam.gserviceaccount.com`
- **Client ID**: `104310228882783091754`
- **Key storage**: Azure Key Vault `flkubi-kv-prd` (resource group `flkubi-prd-rg-001`), secret name `Google-Fluke-ServiceAccount-Json`
- **ADF linked service**: `flkubi_google_bigquery` (`<USER_HOME>/ADF\linkedService\flkubi_google_bigquery.json`)
- **Local key backup**: `<USER_HOME>/Claude\cobalt-cider-279717-service-account.json`

## Authentication — Browser UI
- **Gmail account**: `<USER>@<PERSONAL_DOMAIN>` — created ~2020-2021 for BigQuery console access
- **Login URL**: console.cloud.google.com → select project `cobalt-cider-279717` → BigQuery
- **Password recovery**: Use Google "Forgot password" flow; recovery goes to Gmail recovery options

## History
- **June 2020**: Tom Oyarzun initiated REQ0148060 (Pull GA data to Azure), created GCP project and service account
- **July 2020**: Tom asked Fortive (Glen Hamilton, Michelle Smith) to grant project access to Fortive's BigQuery
- **Oct 2021**: Tom emailed Daniel Sheppard about BigQuery/UA/GA4/GCP data usage for UBI
- **Key people**: Tom Oyarzun (owner), Sunil Kumar (dev, used sunil1.kumar@<ORG_DOMAIN>), Jon Gardiner, Glen Hamilton (Fortive)

## Also Note
- `taashir@gmail.com` is a separate personal Gmail (non-BigQuery, used for personal forwards)
