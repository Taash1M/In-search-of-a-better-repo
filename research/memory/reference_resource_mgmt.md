---
name: reference-resource-mgmt
description: "Scripts and commands for laptop memory audit and process cleanup — temp_memcheck.ps1, process kill patterns"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ae264719-d3c1-4dc1-a2a0-91e65c9ad9e2
---

## Memory Audit Script
- **Path**: `<USER_HOME>/temp_memcheck.ps1`
- **Run**: `powershell.exe -ExecutionPolicy Bypass -File "<USER_HOME>/temp_memcheck.ps1"`
- **Output**: Top 25 processes by aggregated memory, system memory stats, Edge/Chrome/WebView2 totals, all processes >100 MB

## Quick Kill Commands (PowerShell)

### Power Automate Desktop (~500 MB)
```powershell
Stop-Process -Name UIFlowService, PAD.Console.Host, PAD.AutomationServer, Microsoft.Flow.RPA.LogShipper -Force
```
**Note**: UIFlowService is a Windows service and may auto-restart. To prevent:
```powershell
Set-Service -Name "UIFlowService" -StartupType Disabled
```

### Dell TechHub (~573 MB)
```powershell
Stop-Process -Name Dell.TechHub.Instrumentation.SubAgent, Dell.TechHub.DataManager.SubAgent, Dell.TechHub.Analytics.SubAgent -Force
```

## System Memory Check (one-liner)
```powershell
$os = Get-CimInstance Win32_OperatingSystem; Write-Host ("Used: {0:N1} GB / Free: {1:N1} GB / Total: {2:N1} GB" -f (($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/1MB), ($os.FreePhysicalMemory/1MB), ($os.TotalVisibleMemorySize/1MB))
```

## Related
- See [[user-workstation]] for full hardware specs and typical app footprint
