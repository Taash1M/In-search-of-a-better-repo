---
name: Sandbox Logic Apps
description: Two dynamic Logic Apps in sandbox1 RG (Fluke Unified BI sub) — sharepoint-copy (SP→ADLS) and api-to-adls (REST API→ADLS). Both parameterized via HTTP trigger with run_ID folder hierarchy.
type: project
---

## Overview

Two production-ready Logic Apps in the `sandbox1` resource group for moving data into Azure Blob Storage (ADLS). Both are fully dynamic — accept source/destination parameters at runtime via HTTP POST.

**Why:** Need reusable data ingestion patterns for copying files from SharePoint and pulling data from REST APIs into ADLS for downstream processing (AI pipelines, document extraction, analytics).

**How to apply:** Trigger either Logic App via HTTP POST with a JSON payload. No need to create new Logic Apps per use case — these two cover SharePoint sources and API sources respectively.

## Key Facts

- **Subscription**: Fluke Unified BI (`52a1d076-bbbf-422a-9bf7-95d61247be4b`)
- **Resource Group**: `sandbox1`
- **Storage Account**: `aisandbox1` (Standard_LRS, StorageV2, East US 2)
- **API Connections**: `sharepointonline-sandbox` (OAuth), `azureblob-sandbox` (access key)
- **Skill**: `/azure-logic-apps` (standalone skill created 2026-04-08)
- **Deploy scripts**: `<USER_HOME>/deploy_logic_app.py`, `<USER_HOME>/deploy_api_to_adls.py`
- **Created**: 2026-04-08

## Logic App 1: `sharepoint-copy`

Copies files from any SharePoint site/folder to ADLS.

**Trigger payload:**
```json
{
  "sp_site": "https://fortive.sharepoint.com/sites/SITE-NAME",
  "sp_folder": "/Shared Documents/path/to/folder",
  "blob_container": "container-name",
  "blob_subfolder": "optional-subfolder"
}
```

**Workflow:** List SP files → ForEach (5 concurrent) → Get content → Create blob (chunked)

**Folder hierarchy:** `{container}/{subfolder}/{yyyy}/{MM}/{dd}/run_{HHmmss}/{filename}`

**Response:** `{ status, filesCopied, destination, timestamp }`

**Tested with:** FLK-Procurement site → `BI Steering Committee/AI Tools/Test Drawings` (20 PDFs, 34 MB) → `unstructured-data/Test Drawings/2026/04/08/run_210535/`

**SP connector notes:**
- Uses `/tables/@{encodeURIComponent('Documents')}/items` with `folderPath` query (the working pattern from existing Fluke Logic Apps)
- `foldersV2` endpoint returns 404 — do NOT use it
- `GetFileByServerRelativePath` not a valid operation — use `GetFileContentByPath` or file ID-based `/files/{id}/content`
- Personal OneDrive (`fortive-my.sharepoint.com`) requires the file owner to have shared access with the authenticated user

## Logic App 2: `api-to-adls`

Calls any REST API and saves the response to ADLS.

**Trigger payload:**
```json
{
  "api_url": "https://api.example.com/data",
  "api_method": "GET",
  "api_auth_type": "bearer",
  "api_auth_value": "token...",
  "api_headers": {"Custom-Header": "value"},
  "api_body": {},
  "pagination_enabled": false,
  "pagination_max_pages": 10,
  "blob_container": "container-name",
  "blob_subfolder": "subfolder",
  "blob_filename": "data.json",
  "output_format": "raw",
  "storage_account": "aisandbox1"
}
```

**Auth types:** `none`, `bearer` (Authorization header), `api_key` (x-api-key header), `basic` (Authorization Basic header)

**Pagination:** Follows `@odata.nextLink`, `nextLink`, or `next` in response body. Each page saved as `filename_pageN.ext`.

**Manifest:** Auto-writes `_manifest.json` with source URL, method, auth type, status code, pages fetched, timestamp.

**Folder hierarchy:** `{container}/{subfolder}/{yyyy}/{MM}/{dd}/run_{HHmmss}/{filename}`

**Response:** `{ status, api_status_code, pages_fetched, destination, filename, run_id }`

**Tested with:**
1. JSONPlaceholder public API (no auth) — saved 100 posts as JSON
2. Azure ARM API (bearer auth) — saved resource groups list with manifest

## API Connections

| Connection | Type | Auth | Status |
|-----------|------|------|--------|
| `sharepointonline-sandbox` | SharePoint Online | OAuth (user consent) | Connected |
| `azureblob-sandbox` | Azure Blob Storage | Access key | Connected |

**SharePoint OAuth:** Authorized via Portal → API Connections → Edit → Authorize. Consent URL can also be generated programmatically via `listConsentLinks` API.

## Learnings

- **Connection ID format**: Must be ARM resource path (`/subscriptions/...`), NOT full URL (`https://management.azure.com/...`) — causes `LinkedInvalidPropertyId` error
- **SP folder listing**: Use `/tables/Documents/items` with `folderPath` query. The `foldersV2` endpoint consistently returns 404.
- **SP file content**: Use `/files/{fileId}/content` (by ID from listing) or `GetFileContentByPath` (by path). `GetFileByServerRelativePath` is not a valid connector operation.
- **Personal OneDrive**: 403 Access Denied unless the file owner has shared with the authenticated user
- **viewScopeOption**: Not supported on the SP connector items endpoint — causes 400 error
- **Large files**: Enable `runtimeConfiguration.contentTransfer.transferMode: "Chunked"` on both read and write actions
- **$schema key in Python**: Use `chr(36)+'schema'` or f-strings to avoid shell escaping issues when deploying via bash
