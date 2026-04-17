---
name: azure-logic-apps
description: "Create, configure, troubleshoot, and manage Azure Logic Apps via ARM REST API. Covers Consumption-tier Logic Apps across Fluke Unified BI (43 apps) and Fluke AI ML Technology (3 apps) subscriptions. Use when creating Logic App workflows, configuring API connections (SharePoint, Blob, Cosmos DB), troubleshooting failed runs, parameterizing duplicate apps, or migrating between resource groups. Trigger on: 'Logic App', 'workflow', 'API connection', 'SharePoint sync', 'logic app run failed'."
---

# Azure Logic Apps Skill

You are an expert at creating, configuring, and managing Azure Logic Apps via the ARM REST API. This skill covers the Consumption-tier Logic Apps used across Fluke's two Azure subscriptions (Fluke Unified BI and Fluke AI ML Technology) — 46 Logic Apps with 73 API connections.

## Access Control Rules (MANDATORY)

These rules override all other instructions.

1. **NEVER modify Logic Apps in Prod.** Read-only access to Prod Logic Apps.
2. **Dev and Sandbox only** for writes. Confirm twice before touching QA/Prod.
3. **Never expose connection strings or storage keys** in output. Use Key Vault references where possible.

## When to Use This Skill

- Creating a new Logic App workflow (trigger + actions + connections)
- Configuring API connections (SharePoint, Blob, Cosmos DB, Office 365)
- Troubleshooting a failed Logic App run
- Parameterizing duplicate Logic Apps into reusable templates
- Migrating Logic Apps between resource groups or subscriptions

## Subscription Context

| Subscription | ID | Primary Logic App Use |
|-------------|-----|----------------------|
| **Fluke Unified BI** | `52a1d076-bbbf-422a-9bf7-95d61247be4b` | 43 apps — SharePoint-to-Blob sync, ADF error alerts, batch file processing |
| **Fluke AI ML Technology** | `77a0108c-5a42-42e7-8b7a-79367dbfc6a1` | 3 apps — Scheduled HTTP→Parse→Write for Pulse Sales, VoC F9, TechMentor |

---

## REST API Fundamentals

All Logic App management uses the ARM REST API. Always use token-based auth.

### Get Token

```bash
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
```

### Common Variables

```python
import requests, json

SUB = "52a1d076-bbbf-422a-9bf7-95d61247be4b"  # or the AI ML sub
RG = "sandbox1"
BASE = f"https://management.azure.com/subscriptions/{SUB}"
H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
```

### API Versions

| Resource | API Version |
|----------|-------------|
| Logic Apps (workflows) | `2019-05-01` |
| API Connections | `2016-06-01` |
| Managed APIs (connector catalog) | `2016-06-01` |
| Storage Account Keys | `2023-05-01` |

---

## API Connection Management

API connections are **separate ARM resources** from Logic Apps. They hold credentials and must be created before the Logic App references them.

### List Managed APIs (Connector Catalog)

```python
r = requests.get(f"{BASE}/providers/Microsoft.Web/locations/eastus2/managedApis?api-version=2016-06-01", headers=H)
for api in r.json()["value"]:
    print(f'{api["name"]}: {list(api["properties"].get("connectionParameters", {}).keys())}')
```

### Connectors Used at Fluke

| Connector | API Name | Auth Type | Used By |
|-----------|----------|-----------|---------|
| **Azure Blob Storage** | `azureblob` | Access Key | 40 Logic Apps |
| **SharePoint Online** | `sharepointonline` | OAuth (token) | 33 Logic Apps |
| **Cosmos DB** | `documentdb` | Account Key | 16 Logic Apps |
| **OneDrive for Business** | `onedriveforbusiness` | OAuth (token) | 12 Logic Apps |
| **Office 365 Outlook** | `office365` | OAuth (token) | 1 Logic App |
| **SMTP** | `smtp` | Username/Password | 1 Logic App |
| **Adobe PDF Tools** | `adobepdftools` | API Key | 1 Logic App |
| **SQL Server** | `sql` | Connection String | 1 Logic App |

### Create Azure Blob Storage Connection (Key-Based)

```python
# Get storage account key
r = requests.post(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Storage/storageAccounts/{ACCOUNT}/listKeys?api-version=2023-05-01",
    headers=H
)
key = r.json()["keys"][0]["value"]

# Create connection
body = {
    "location": "eastus2",
    "properties": {
        "displayName": f"azureblob-{RG}",
        "api": {
            "id": f"/subscriptions/{SUB}/providers/Microsoft.Web/locations/eastus2/managedApis/azureblob"
        },
        "parameterValues": {
            "accountName": ACCOUNT,
            "accessKey": key
        }
    }
}
r = requests.put(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Web/connections/azureblob-{RG}?api-version=2016-06-01",
    headers=H, json=body
)
# Expect 201 Created
```

### Create SharePoint Online Connection (OAuth)

SharePoint requires user consent after creation.

```python
# Step 1: Create the connection shell
body = {
    "location": "eastus2",
    "properties": {
        "displayName": f"sharepointonline-{RG}",
        "api": {
            "id": f"/subscriptions/{SUB}/providers/Microsoft.Web/locations/eastus2/managedApis/sharepointonline"
        }
    }
}
r = requests.put(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Web/connections/sharepointonline-{RG}?api-version=2016-06-01",
    headers=H, json=body
)
# Status will be "Unauthenticated" — needs consent

# Step 2: Get consent URL
r = requests.post(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Web/connections/sharepointonline-{RG}/listConsentLinks?api-version=2016-06-01",
    headers=H,
    json={"parameters": [{"parameterName": "token", "redirectUrl": "https://portal.azure.com"}]}
)
consent_url = r.json()["value"][0]["link"]
# User must open this URL in browser and sign in

# Step 3: After user consents, confirm connection
r = requests.post(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Web/connections/sharepointonline-{RG}/confirmConsentCode?api-version=2016-06-01",
    headers=H,
    json={"code": "<code-from-redirect>", "objectId": "<user-object-id>", "tenantId": "0f634ac3-b39f-41a6-83ba-8f107876c692"}
)
```

**Shortcut:** Tell user to authorize via Portal → API Connections → Edit → Authorize. This is faster than programmatic consent for one-time setup.

### Create Cosmos DB Connection

```python
body = {
    "location": "eastus2",
    "properties": {
        "displayName": f"cosmosdb-{RG}",
        "api": {
            "id": f"/subscriptions/{SUB}/providers/Microsoft.Web/locations/eastus2/managedApis/documentdb"
        },
        "parameterValues": {
            "databaseAccount": COSMOS_ACCOUNT,
            "accessKey": COSMOS_KEY
        }
    }
}
```

### Check Connection Status

```python
r = requests.get(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Web/connections/{CONN_NAME}?api-version=2016-06-01",
    headers=H
)
statuses = r.json()["properties"].get("statuses", [])
for s in statuses:
    print(f'{s["status"]}: {s.get("error", {}).get("message", "OK")}')
```

---

## Connection ID Format

**Critical:** When referencing connections in Logic App definitions, use the ARM resource path — NOT a full URL.

```python
# CORRECT — resource path
conn_id = f"/subscriptions/{SUB}/resourceGroups/{RG}/providers/Microsoft.Web/connections/{CONN_NAME}"

# WRONG — full URL (causes LinkedInvalidPropertyId error)
conn_id = f"https://management.azure.com/subscriptions/{SUB}/providers/..."

# API ID (for managed API reference)
api_id = f"/subscriptions/{SUB}/providers/Microsoft.Web/locations/eastus2/managedApis/{API_NAME}"
```

---

## Workflow Definition Structure

Every Logic App workflow follows this JSON structure:

```json
{
  "location": "eastus2",
  "properties": {
    "state": "Enabled",
    "definition": {
      "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
        "$connections": { "defaultValue": {}, "type": "Object" }
      },
      "triggers": { ... },
      "actions": { ... },
      "outputs": {}
    },
    "parameters": {
      "$connections": {
        "value": {
          "azureblob": {
            "connectionId": "/subscriptions/.../connections/azureblob-sandbox",
            "connectionName": "azureblob-sandbox",
            "id": "/subscriptions/.../managedApis/azureblob"
          }
        }
      }
    }
  }
}
```

**Key rules:**
- `definition.parameters` declares parameter types (always include `$connections`)
- `properties.parameters` provides the actual values (connection IDs)
- Triggers and actions reference connections via `@parameters('$connections')['connName']['connectionId']`
- In Python, escape `$` as `\\$` in f-strings or use raw strings

### Deploy Workflow

```python
r = requests.put(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows/{LA_NAME}?api-version=2019-05-01",
    headers=H, json=workflow_body
)
# 200 = updated, 201 = created
```

---

## The 5 Workflow Templates

These cover every pattern used across Fluke's 46 Logic Apps.

### Template 1: SharePoint → Blob Sync (File Trigger)

The most common pattern (~20 apps). Copies files from SharePoint to Blob Storage when created or modified.

```python
def sharepoint_to_blob_workflow(sub, rg, sp_site, sp_library, blob_account, blob_container, sp_conn, blob_conn):
    """Generate a SharePoint-to-Blob sync Logic App definition.
    
    Args:
        sp_site: SharePoint site URL (e.g., 'https://fortive.sharepoint.com/sites/FlukeLegal')
        sp_library: Document library path (e.g., '/Shared Documents/Contracts')
        blob_account: Storage account name
        blob_container: Target container name
        sp_conn: SharePoint connection name
        blob_conn: Blob connection name
    """
    return {
        "location": "eastus2",
        "properties": {
            "state": "Enabled",
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"}
                },
                "triggers": {
                    "When_a_file_is_created_or_modified": {
                        "type": "ApiConnection",
                        "inputs": {
                            "host": {
                                "connection": {
                                    "name": f"@parameters('$connections')['{sp_conn}']['connectionId']"
                                }
                            },
                            "method": "get",
                            "path": f"/datasets/@{{encodeURIComponent(encodeURIComponent('{sp_site}'))}}/triggers/onupdatedfile",
                            "queries": {
                                "folderId": sp_library,
                                "includeFileContent": True,
                                "inferContentType": True
                            }
                        },
                        "recurrence": {"frequency": "Minute", "interval": 5},
                        "splitOn": "@triggerBody()"
                    }
                },
                "actions": {
                    "Create_blob": {
                        "type": "ApiConnection",
                        "inputs": {
                            "host": {
                                "connection": {
                                    "name": f"@parameters('$connections')['{blob_conn}']['connectionId']"
                                }
                            },
                            "method": "post",
                            "path": f"/v2/datasets/@{{encodeURIComponent(encodeURIComponent('{blob_account}'))}}/files",
                            "queries": {
                                "folderPath": f"/{blob_container}",
                                "name": "@triggerOutputs()['headers']['x-ms-file-name']",
                                "queryParametersSingleEncoded": True
                            },
                            "body": "@triggerBody()"
                        },
                        "runAfter": {},
                        "runtimeConfiguration": {
                            "contentTransfer": {"transferMode": "Chunked"}
                        }
                    }
                },
                "outputs": {}
            },
            "parameters": {
                "$connections": {
                    "value": _connection_params(sub, rg, {
                        sp_conn: "sharepointonline",
                        blob_conn: "azureblob"
                    })
                }
            }
        }
    }
```

### Template 2: Batch File Listing + Sync (Recurrence)

Used by 5730A, TechSupport, SiteGPT — scheduled sync of entire libraries with Cosmos DB indexing.

```python
def batch_sync_workflow(sub, rg, sp_site, sp_library, blob_account, blob_container, cosmos_db, cosmos_collection, sp_conn, blob_conn, cosmos_conn):
    """Scheduled batch sync: list SP files → copy to Blob → index in Cosmos DB."""
    return {
        "location": "eastus2",
        "properties": {
            "state": "Enabled",
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"}
                },
                "triggers": {
                    "Recurrence": {
                        "type": "Recurrence",
                        "recurrence": {"frequency": "Hour", "interval": 6}
                    }
                },
                "actions": {
                    "List_files_in_folder": {
                        "type": "ApiConnection",
                        "inputs": {
                            "host": {
                                "connection": {
                                    "name": f"@parameters('$connections')['{sp_conn}']['connectionId']"
                                }
                            },
                            "method": "get",
                            "path": f"/datasets/@{{encodeURIComponent(encodeURIComponent('{sp_site}'))}}/foldersV2/@{{encodeURIComponent(encodeURIComponent('{sp_library}'))}}/files",
                            "queries": {"skipToken": "", "top": 500}
                        },
                        "runAfter": {}
                    },
                    "For_each_file": {
                        "type": "Foreach",
                        "foreach": "@body('List_files_in_folder')['value']",
                        "actions": {
                            "Get_file_content": {
                                "type": "ApiConnection",
                                "inputs": {
                                    "host": {
                                        "connection": {
                                            "name": f"@parameters('$connections')['{sp_conn}']['connectionId']"
                                        }
                                    },
                                    "method": "get",
                                    "path": f"/datasets/@{{encodeURIComponent(encodeURIComponent('{sp_site}'))}}/files/@{{encodeURIComponent(items('For_each_file')?['Id'])}}/content"
                                },
                                "runAfter": {}
                            },
                            "Create_or_update_blob": {
                                "type": "ApiConnection",
                                "inputs": {
                                    "host": {
                                        "connection": {
                                            "name": f"@parameters('$connections')['{blob_conn}']['connectionId']"
                                        }
                                    },
                                    "method": "post",
                                    "path": f"/v2/datasets/@{{encodeURIComponent(encodeURIComponent('{blob_account}'))}}/files",
                                    "queries": {
                                        "folderPath": f"/{blob_container}",
                                        "name": "@items('For_each_file')?['Name']",
                                        "queryParametersSingleEncoded": True
                                    },
                                    "body": "@body('Get_file_content')"
                                },
                                "runAfter": {"Get_file_content": ["Succeeded"]}
                            },
                            "Create_or_update_Cosmos_doc": {
                                "type": "ApiConnection",
                                "inputs": {
                                    "host": {
                                        "connection": {
                                            "name": f"@parameters('$connections')['{cosmos_conn}']['connectionId']"
                                        }
                                    },
                                    "method": "post",
                                    "path": f"/v2/cosmosdb/@{{encodeURIComponent('{cosmos_db}')}}/colls/@{{encodeURIComponent('{cosmos_collection}')}}/docs",
                                    "body": {
                                        "id": "@items('For_each_file')?['Id']",
                                        "fileName": "@items('For_each_file')?['Name']",
                                        "filePath": "@items('For_each_file')?['Path']",
                                        "lastModified": "@items('For_each_file')?['LastModified']",
                                        "blobPath": f"@{{concat('{blob_container}/', items('For_each_file')?['Name'])}}"
                                    }
                                },
                                "runAfter": {"Create_or_update_blob": ["Succeeded"]}
                            }
                        },
                        "runAfter": {"List_files_in_folder": ["Succeeded"]},
                        "runtimeConfiguration": {"concurrency": {"repetitions": 5}}
                    }
                },
                "outputs": {}
            },
            "parameters": {
                "$connections": {
                    "value": _connection_params(sub, rg, {
                        sp_conn: "sharepointonline",
                        blob_conn: "azureblob",
                        cosmos_conn: "documentdb"
                    })
                }
            }
        }
    }
```

### Template 3: Delete Cascade

When a SharePoint file is deleted, remove the matching blob and Cosmos DB index entry.

```python
def delete_cascade_workflow(sub, rg, sp_site, sp_library, blob_account, blob_container, cosmos_db, cosmos_collection, sp_conn, blob_conn, cosmos_conn):
    """Delete cascade: SP file deleted → delete blob + Cosmos doc."""
    return {
        "location": "eastus2",
        "properties": {
            "state": "Enabled",
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"}
                },
                "triggers": {
                    "When_a_file_is_deleted": {
                        "type": "ApiConnection",
                        "inputs": {
                            "host": {
                                "connection": {
                                    "name": f"@parameters('$connections')['{sp_conn}']['connectionId']"
                                }
                            },
                            "method": "get",
                            "path": f"/datasets/@{{encodeURIComponent(encodeURIComponent('{sp_site}'))}}/triggers/ondeletedfile",
                            "queries": {"folderId": sp_library}
                        },
                        "recurrence": {"frequency": "Minute", "interval": 5}
                    }
                },
                "actions": {
                    "Delete_blob": {
                        "type": "ApiConnection",
                        "inputs": {
                            "host": {
                                "connection": {
                                    "name": f"@parameters('$connections')['{blob_conn}']['connectionId']"
                                }
                            },
                            "method": "delete",
                            "path": f"/v2/datasets/@{{encodeURIComponent(encodeURIComponent('{blob_account}'))}}/files/@{{encodeURIComponent(encodeURIComponent(concat('/{blob_container}/', triggerOutputs()['headers']['x-ms-file-name'])))}}"
                        },
                        "runAfter": {}
                    },
                    "Delete_Cosmos_doc": {
                        "type": "ApiConnection",
                        "inputs": {
                            "host": {
                                "connection": {
                                    "name": f"@parameters('$connections')['{cosmos_conn}']['connectionId']"
                                }
                            },
                            "method": "delete",
                            "path": f"/v2/cosmosdb/@{{encodeURIComponent('{cosmos_db}')}}/colls/@{{encodeURIComponent('{cosmos_collection}')}}/docs/@{{encodeURIComponent(triggerOutputs()['headers']['x-ms-file-id'])}}"
                        },
                        "runAfter": {"Delete_blob": ["Succeeded", "Failed"]}
                    }
                },
                "outputs": {}
            },
            "parameters": {
                "$connections": {
                    "value": _connection_params(sub, rg, {
                        sp_conn: "sharepointonline",
                        blob_conn: "azureblob",
                        cosmos_conn: "documentdb"
                    })
                }
            }
        }
    }
```

### Template 4: HTTP-Triggered Utility

Manual or ADF-triggered Logic App for on-demand operations.

```python
def http_trigger_workflow(sub, rg, actions_dict, connections_dict):
    """HTTP-triggered Logic App for on-demand operations.
    
    Args:
        actions_dict: Dict of action definitions (varies per use case)
        connections_dict: Dict mapping conn_name → api_name
    """
    return {
        "location": "eastus2",
        "properties": {
            "state": "Enabled",
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"}
                },
                "triggers": {
                    "manual": {
                        "type": "Request",
                        "kind": "Http",
                        "inputs": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "source_path": {"type": "string"},
                                    "destination_path": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "actions": actions_dict,
                "outputs": {}
            },
            "parameters": {
                "$connections": {
                    "value": _connection_params(sub, rg, connections_dict)
                }
            }
        }
    }
```

### Template 5: Scheduled HTTP → Parse → Write (AI ML Pattern)

Used by Pulse Sales, VoC F9, TechMentor — calls an API on schedule, parses response, writes to multiple destinations.

```python
def scheduled_api_workflow(sub, rg, api_url, api_headers, sp_site, sp_folder, blob_account, blob_container, sp_conn, blob_conn, schedule_hours=6):
    """Scheduled API call → parse JSON → write to SharePoint + Blob."""
    return {
        "location": "eastus2",
        "properties": {
            "state": "Enabled",
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "$connections": {"defaultValue": {}, "type": "Object"}
                },
                "triggers": {
                    "Recurrence": {
                        "type": "Recurrence",
                        "recurrence": {"frequency": "Hour", "interval": schedule_hours}
                    }
                },
                "actions": {
                    "Call_API": {
                        "type": "Http",
                        "inputs": {
                            "method": "GET",
                            "uri": api_url,
                            "headers": api_headers
                        },
                        "runAfter": {}
                    },
                    "Parse_JSON": {
                        "type": "ParseJson",
                        "inputs": {
                            "content": "@body('Call_API')",
                            "schema": {"type": "object"}
                        },
                        "runAfter": {"Call_API": ["Succeeded"]}
                    },
                    "For_each_result": {
                        "type": "Foreach",
                        "foreach": "@body('Parse_JSON')?['results']",
                        "actions": {
                            "Create_file_in_SharePoint": {
                                "type": "ApiConnection",
                                "inputs": {
                                    "host": {
                                        "connection": {
                                            "name": f"@parameters('$connections')['{sp_conn}']['connectionId']"
                                        }
                                    },
                                    "method": "post",
                                    "path": f"/datasets/@{{encodeURIComponent(encodeURIComponent('{sp_site}'))}}/files",
                                    "queries": {"folderPath": sp_folder, "name": "@items('For_each_result')?['id']"},
                                    "body": "@items('For_each_result')"
                                },
                                "runAfter": {}
                            },
                            "Create_blob_copy": {
                                "type": "ApiConnection",
                                "inputs": {
                                    "host": {
                                        "connection": {
                                            "name": f"@parameters('$connections')['{blob_conn}']['connectionId']"
                                        }
                                    },
                                    "method": "post",
                                    "path": f"/v2/datasets/@{{encodeURIComponent(encodeURIComponent('{blob_account}'))}}/files",
                                    "queries": {
                                        "folderPath": f"/{blob_container}",
                                        "name": "@items('For_each_result')?['id']",
                                        "queryParametersSingleEncoded": True
                                    },
                                    "body": "@items('For_each_result')"
                                },
                                "runAfter": {}
                            }
                        },
                        "runAfter": {"Parse_JSON": ["Succeeded"]},
                        "runtimeConfiguration": {"concurrency": {"repetitions": 10}}
                    }
                },
                "outputs": {}
            },
            "parameters": {
                "$connections": {
                    "value": _connection_params(sub, rg, {
                        sp_conn: "sharepointonline",
                        blob_conn: "azureblob"
                    })
                }
            }
        }
    }
```

### Helper: Connection Parameters Builder

```python
def _connection_params(sub, rg, conn_map):
    """Build $connections parameter value from a dict of {conn_name: api_name}.
    
    Args:
        conn_map: {"azureblob-sandbox": "azureblob", "sharepointonline-sandbox": "sharepointonline"}
    """
    result = {}
    for conn_name, api_name in conn_map.items():
        result[conn_name] = {
            "connectionId": f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Web/connections/{conn_name}",
            "connectionName": conn_name,
            "id": f"/subscriptions/{sub}/providers/Microsoft.Web/locations/eastus2/managedApis/{api_name}"
        }
    return result
```

---

## SharePoint Path Formats

SharePoint paths differ between corporate sites and personal OneDrive.

### Corporate SharePoint Site
```
Site URL:    https://fortive.sharepoint.com/sites/FlukeLegal
Library:     /Shared Documents/Contracts
Encoded:     @{encodeURIComponent(encodeURIComponent('https://fortive.sharepoint.com/sites/FlukeLegal'))}
```

### Personal OneDrive (fortive-my.sharepoint.com)
```
Site URL:    https://fortive-my.sharepoint.com/personal/paul_hollewijn_fluke_com
File path:   /personal/paul_hollewijn_fluke_com/Documents/Recordings/filename.mp4
Note:        Email dots/@ replaced with underscores in the personal site URL
```

### Path Encoding Rule
SharePoint paths in Logic App actions must be **double-encoded**:
```
@{encodeURIComponent(encodeURIComponent('https://fortive.sharepoint.com/sites/MySite'))}
```

This is because Logic Apps auto-decodes once, and the SharePoint API expects an encoded URL.

---

## Operations

### List All Logic Apps in a Resource Group

```python
r = requests.get(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows?api-version=2019-05-01",
    headers=H
)
for la in r.json()["value"]:
    state = la["properties"]["state"]
    triggers = list(la["properties"]["definition"].get("triggers", {}).keys())
    print(f'{la["name"]}: {state}, triggers={triggers}')
```

### Get Trigger Callback URL (for HTTP triggers)

```python
r = requests.post(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows/{LA_NAME}/triggers/manual/listCallbackUrl?api-version=2019-05-01",
    headers=H
)
trigger_url = r.json()["value"]
# POST to this URL to trigger the Logic App (no auth needed — URL contains SAS token)
```

### Run a Logic App Manually

```python
# For HTTP-triggered Logic Apps, POST to the trigger URL
r = requests.post(trigger_url, json={"source_path": "/docs/file.pdf"})

# For non-HTTP triggers, use the run endpoint
r = requests.post(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows/{LA_NAME}/triggers/{TRIGGER_NAME}/run?api-version=2019-05-01",
    headers=H
)
```

### Check Run History

```python
r = requests.get(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows/{LA_NAME}/runs?api-version=2019-05-01&$top=10",
    headers=H
)
for run in r.json()["value"]:
    status = run["properties"]["status"]
    start = run["properties"]["startTime"]
    trigger = run["properties"]["trigger"]["name"]
    print(f'{run["name"]}: {status} at {start} via {trigger}')
```

### Get Failed Run Details

```python
# Get run actions to find which step failed
run_id = "08585..."
r = requests.get(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows/{LA_NAME}/runs/{run_id}/actions?api-version=2019-05-01",
    headers=H
)
for action in r.json()["value"]:
    props = action["properties"]
    if props["status"] == "Failed":
        print(f'FAILED: {action["name"]}')
        print(f'  Code: {props.get("code")}')
        print(f'  Error: {props.get("error", {}).get("message")}')
        # Get input/output for debugging
        if "inputsLink" in props:
            inputs = requests.get(props["inputsLink"]["uri"]).json()
            print(f'  Input: {json.dumps(inputs, indent=2)[:500]}')
```

### Enable / Disable a Logic App

```python
# Disable
requests.post(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows/{LA_NAME}/disable?api-version=2019-05-01",
    headers=H
)

# Enable
requests.post(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows/{LA_NAME}/enable?api-version=2019-05-01",
    headers=H
)
```

### Export Workflow Definition (Backup)

```python
r = requests.get(
    f"{BASE}/resourceGroups/{RG}/providers/Microsoft.Logic/workflows/{LA_NAME}?api-version=2019-05-01",
    headers=H
)
with open(f"{LA_NAME}_backup.json", "w") as f:
    json.dump(r.json(), f, indent=2)
```

---

## Parameterization Pattern (Reducing Duplication)

The 5730A project has 3 near-identical Logic Apps per document library (get-all, get-updated, delete). This pattern collapses them into one parameterized definition.

### Before: 3 Separate Logic Apps
```
5730A-library1-get-all        → Recurrence → List all → Copy to Blob + Cosmos
5730A-library1-get-updated    → File trigger → Copy changed file
5730A-library1-delete          → Delete trigger → Delete blob + Cosmos doc
```

### After: 1 Parameterized Template

```python
def create_document_sync_suite(sub, rg, project_name, sp_site, sp_library, blob_account, blob_container, cosmos_db, cosmos_collection):
    """Create a complete sync suite (3 Logic Apps) for a document library."""
    
    sp_conn = f"sharepointonline-{project_name}"
    blob_conn = f"azureblob-{project_name}"
    cosmos_conn = f"cosmosdb-{project_name}"
    
    apps = {
        f"{project_name}-get-all": batch_sync_workflow(
            sub, rg, sp_site, sp_library, blob_account, blob_container,
            cosmos_db, cosmos_collection, sp_conn, blob_conn, cosmos_conn
        ),
        f"{project_name}-get-updated": sharepoint_to_blob_workflow(
            sub, rg, sp_site, sp_library, blob_account, blob_container,
            sp_conn, blob_conn
        ),
        f"{project_name}-delete": delete_cascade_workflow(
            sub, rg, sp_site, sp_library, blob_account, blob_container,
            cosmos_db, cosmos_collection, sp_conn, blob_conn, cosmos_conn
        ),
    }
    
    results = {}
    for name, definition in apps.items():
        r = requests.put(
            f"{BASE}/resourceGroups/{rg}/providers/Microsoft.Logic/workflows/{name}?api-version=2019-05-01",
            headers=H, json=definition
        )
        results[name] = r.status_code
    return results
```

---

## Large File Handling

Logic Apps have a **100 MB** action content limit. For files larger than 100 MB (like the MP4 in the sharepoint-copy use case):

### Enable Chunked Transfer

Add `runtimeConfiguration` to the action:

```json
"runtimeConfiguration": {
    "contentTransfer": {
        "transferMode": "Chunked"
    }
}
```

### For Very Large Files (>100 MB)

Use the **Get file content using path** action with chunking enabled, or break into:
1. Get file metadata (no content)
2. Generate a SAS URL for the blob destination
3. Use HTTP action to stream directly from SharePoint to Blob via SAS

---

## Troubleshooting

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `LinkedInvalidPropertyId` | Full URL used instead of resource path in `api.id` | Use `/subscriptions/...` format, not `https://management.azure.com/...` |
| `Unauthenticated` on SharePoint connection | OAuth consent not completed | Authorize via Portal → API Connections → Edit → Authorize |
| `The file was not found` | Incorrect SharePoint path or encoding | Double-encode the site URL, verify file exists |
| `ActionFailed` with 403 | Connection lacks permissions | Re-authorize connection with account that has access |
| `TriggerHistoryNotFound` | Trigger hasn't fired yet | Check trigger conditions, verify recurrence schedule |
| `RequestTooLarge` | File exceeds 100 MB limit | Enable chunked transfer mode |
| `InvalidTemplate` | Malformed expression in definition | Check `@` expression syntax, escape single quotes |

### Expression Syntax Quick Reference

```
@triggerBody()                              — Trigger output body
@triggerOutputs()['headers']['x-ms-file-name']  — Trigger response header
@body('Action_Name')                        — Action output body
@items('For_each_name')                     — Current item in ForEach
@parameters('$connections')['conn']['connectionId']  — Connection reference
@encodeURIComponent(value)                  — URL encode
@concat('path/', variables('fileName'))     — String concatenation
@utcNow()                                   — Current UTC timestamp
```

---

## 10 NEVER Rules

1. **NEVER hardcode storage keys in Logic App definitions.** Use API connections (which store keys in the connection resource) or Key Vault references.
2. **NEVER use single encoding for SharePoint site URLs.** Always double-encode: `@{encodeURIComponent(encodeURIComponent('...'))}`.
3. **NEVER deploy to Prod without testing in Dev first.** Export the Dev definition, change connection references, deploy to Prod.
4. **NEVER delete an API connection that's used by running Logic Apps.** Check references first: list all workflows and search for the connection name.
5. **NEVER set ForEach concurrency above 20.** Default is 20, max is 50 — but high concurrency + API rate limits = cascading failures.
6. **NEVER assume trigger fires immediately.** Polling triggers (SharePoint file events) check on the recurrence interval. A 5-minute interval means up to 5 minutes delay.
7. **NEVER skip error handling for multi-step workflows.** Use `runAfter` with `["Succeeded", "Failed"]` for cleanup actions that must always run.
8. **NEVER use the full `https://management.azure.com/` prefix** in connection IDs or API IDs. Use resource paths starting with `/subscriptions/`.
9. **NEVER process files >100 MB without chunked transfer mode.** Logic Apps silently truncate content beyond the limit.
10. **NEVER create duplicate API connections per resource group.** Reuse existing connections — check with a list call first.
