---
name: ubi-medallion-patterns
description: "UBI medallion-architecture patterns learned — all-purpose clusters, Oracle EBS entity prefixes, VARCHAR2→STRING in Bronze, Silver type-cast/joins, Gold backtick aliases, ADLS direct mirror"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

# UBI Medallion Patterns Learned

- **Always use all-purpose clusters** for Databricks interactive/notebook work
- Oracle EBS columns use entity prefixes (OOHA=headers, OOLA=lines, MSIB=items, HCA/HCP/HCSUA=customers)
- All Oracle VARCHAR2 fields land as STRING in Bronze
- Silver layer does type casting, business logic, JOINs to ~25 dimension tables
- Gold layer creates views with business-friendly aliases (backtick-quoted in Spark SQL)
- ADLS publish is a direct mirror of Gold views in Delta format

Related: [[ubi-platform-key-facts]] · [[so-backlog-stream-specifics]]
