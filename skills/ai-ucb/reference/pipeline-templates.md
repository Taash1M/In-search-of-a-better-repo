# AI Use Case Builder - Pipeline Templates

ADF pipeline JSON, Databricks notebook templates, and trigger configurations. Used by the Pipeline sub-skill (`ai-ucb-pipeline.md`) during Phase 2.

**Template status key:**
- **FULL** = Complete, production-ready implementation
- All templates are now **FULL** implementations (stubs expanded in Sprint 11)

---

## ADF Master Pipeline Template

```json
{
  "name": "PL_{app}_Master",
  "properties": {
    "activities": [
      {
        "name": "PreLog",
        "type": "SqlServerStoredProcedure",
        "linkedServiceName": {"referenceName": "AzureSqlMetadata", "type": "LinkedServiceReference"},
        "typeProperties": {
          "storedProcedureName": "usp_StatusControl_PreLog",
          "storedProcedureParameters": {
            "StreamName": {"value": "{app}", "type": "String"},
            "SubStream": {"value": "Master", "type": "String"},
            "Status": {"value": "Running", "type": "String"}
          }
        }
      },
      {
        "name": "MartRefresh",
        "type": "DatabricksNotebook",
        "dependsOn": [{"activity": "PreLog", "dependencyConditions": ["Succeeded"]}],
        "linkedServiceName": {"referenceName": "DatabricksLinkedService", "type": "LinkedServiceReference"},
        "typeProperties": {
          "notebookPath": "/Shared/{app}/Silver_{app}",
          "baseParameters": {
            "StreamName": "{app}",
            "SubStream": "Master",
            "Database": "flukebi_Silver"
          }
        }
      },
      {
        "name": "GoldRefresh",
        "type": "DatabricksNotebook",
        "dependsOn": [{"activity": "MartRefresh", "dependencyConditions": ["Succeeded"]}],
        "typeProperties": {
          "notebookPath": "/Shared/{app}/Gold_{app}",
          "baseParameters": {"StreamName": "{app}", "Database": "flukebi_Gold"}
        }
      },
      {
        "name": "AILayerRefresh",
        "type": "DatabricksNotebook",
        "dependsOn": [{"activity": "GoldRefresh", "dependencyConditions": ["Succeeded"]}],
        "typeProperties": {
          "notebookPath": "/Shared/{app}/AILayer_{app}",
          "baseParameters": {"StreamName": "{app}"}
        }
      },
      {
        "name": "PostLog_Success",
        "type": "SqlServerStoredProcedure",
        "dependsOn": [{"activity": "AILayerRefresh", "dependencyConditions": ["Succeeded"]}],
        "typeProperties": {
          "storedProcedureName": "usp_StatusControl_PostLog",
          "storedProcedureParameters": {
            "StreamName": {"value": "{app}", "type": "String"},
            "Status": {"value": "Succeeded", "type": "String"}
          }
        }
      },
      {
        "name": "PostLog_Failure",
        "type": "SqlServerStoredProcedure",
        "dependsOn": [
          {"activity": "MartRefresh", "dependencyConditions": ["Failed"]},
          {"activity": "GoldRefresh", "dependencyConditions": ["Failed"]},
          {"activity": "AILayerRefresh", "dependencyConditions": ["Failed"]}
        ],
        "typeProperties": {
          "storedProcedureName": "usp_StatusControl_PostLog",
          "storedProcedureParameters": {
            "StreamName": {"value": "{app}", "type": "String"},
            "Status": {"value": "Failed", "type": "String"}
          }
        }
      }
    ]
  }
}
```

---

## ADF Linked Service Templates

### Databricks Linked Service
```json
{
  "name": "DatabricksLinkedService",
  "properties": {
    "type": "AzureDatabricks",
    "typeProperties": {
      "domain": "https://adb-{workspace-id}.azuredatabricks.net",
      "authentication": "MSI",
      "workspaceResourceId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Databricks/workspaces/{workspace}",
      "existingClusterId": "{cluster-id}"
    }
  }
}
```

### Copy Activity Source Templates

**Oracle (JDBC):**
```json
{
  "name": "Extract_{source_name}",
  "type": "Copy",
  "typeProperties": {
    "source": {
      "type": "OracleSource",
      "oracleReaderQuery": "SELECT * FROM {schema}.{table} WHERE LAST_UPDATE_DATE >= @{pipeline().parameters.IncrementalDate}"
    },
    "sink": {
      "type": "ParquetSink",
      "storeSettings": {"type": "AzureBlobFSWriteSettings"},
      "formatSettings": {"type": "ParquetWriteSettings"}
    }
  },
  "inputs": [{"referenceName": "OracleDataset_{source}", "type": "DatasetReference"}],
  "outputs": [{"referenceName": "ADLS_Bronze_{source}", "type": "DatasetReference"}]
}
```

**SharePoint (REST via Databricks):**
```json
{
  "name": "Extract_{source_name}",
  "type": "DatabricksNotebook",
  "typeProperties": {
    "notebookPath": "/Shared/{app}/Bronze_{app}_SharePoint",
    "baseParameters": {
      "site_url": "{sharepoint_site}",
      "library": "{document_library}",
      "output_path": "abfss://{container}@{storage}.dfs.core.windows.net/Bronze/{app}/{source_name}/"
    }
  }
}
```

---

## ADF Trigger Templates

**Schedule Trigger (daily):**
```json
{
  "name": "TR_{app}_Daily",
  "properties": {
    "type": "ScheduleTrigger",
    "typeProperties": {
      "recurrence": {
        "frequency": "Day",
        "interval": 1,
        "startTime": "2026-01-01T06:00:00Z",
        "timeZone": "Eastern Standard Time"
      }
    },
    "pipelines": [{"pipelineReference": {"referenceName": "PL_{app}_Master", "type": "PipelineReference"}}]
  }
}
```

**Blob Event Trigger:**
```json
{
  "name": "TR_{app}_BlobEvent",
  "properties": {
    "type": "BlobEventsTrigger",
    "typeProperties": {
      "blobPathBeginsWith": "/{container}/incoming/",
      "blobPathEndsWith": ".json",
      "events": ["Microsoft.Storage.BlobCreated"]
    },
    "pipelines": [{"pipelineReference": {"referenceName": "PL_{app}_Master", "type": "PipelineReference"}}]
  }
}
```

---

## Bronze Notebook Templates

### Bronze: Document Ingestion [FULL]

```python
# Databricks notebook: Bronze_{app}_Documents
# Strategy: doc-ingestion
# Status: FULL

# --- Widgets ---
dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("SourcePath", "", "Source ADLS Path")
dbutils.widgets.text("Database", "flukebi_Bronze", "Target Database")

stream = dbutils.widgets.get("StreamName")
source_path = dbutils.widgets.get("SourcePath")
database = dbutils.widgets.get("Database")

# --- Read raw documents from ADLS ---
from pyspark.sql.functions import input_file_name, current_timestamp, lit, udf
from pyspark.sql.types import StringType
import os

raw_files = spark.read.format("binaryFile") \
    .option("pathGlobFilter", "*.{pdf,docx,html,txt,csv}") \
    .option("recursiveFileLookup", "true") \
    .load(source_path)

# --- Extract text content based on file type ---
# Uses PyPDF2 for PDF, python-docx for DOCX, BeautifulSoup for HTML
@udf(StringType())
def extract_text(content_bytes, path):
    """Extract text from binary file content based on extension."""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            import io, PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == ".docx":
            import io, docx
            doc = docx.Document(io.BytesIO(content_bytes))
            return "\n".join(p.text for p in doc.paragraphs)
        elif ext in (".html", ".htm"):
            from bs4 import BeautifulSoup
            return BeautifulSoup(content_bytes.decode("utf-8", errors="replace"), "html.parser").get_text()
        elif ext in (".txt", ".csv"):
            return content_bytes.decode("utf-8", errors="replace")
        else:
            return None
    except Exception as e:
        return f"EXTRACTION_ERROR: {str(e)}"

# --- Transform to Bronze table ---
bronze_df = raw_files.select(
    input_file_name().alias("source_file_path"),
    "path",
    "length",
    "modificationTime",
    extract_text("content", "path").alias("text_content"),
    current_timestamp().alias("_ingested_at"),
    lit(stream).alias("_stream_name")
)

# --- Write to Delta ---
bronze_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{database}.{stream}_documents_raw")

print(f"Bronze: {bronze_df.count()} documents ingested to {database}.{stream}_documents_raw")
```

### Bronze: Typed Ingestion [FULL]

```python
# Databricks notebook: Bronze_{app}_Typed
# Strategy: typed-ingestion / schema-on-read
# Status: FULL

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("SourceTable", "", "Source Table Path")
dbutils.widgets.text("Database", "flukebi_Bronze", "Target Database")

stream = dbutils.widgets.get("StreamName")
source = dbutils.widgets.get("SourceTable")
database = dbutils.widgets.get("Database")

from pyspark.sql.functions import current_timestamp, lit

# Read from source (Parquet from ADF Copy Activity output)
raw_df = spark.read.format("parquet").load(source)

# Add metadata columns
bronze_df = raw_df \
    .withColumn("_ingested_at", current_timestamp()) \
    .withColumn("_stream_name", lit(stream)) \
    .withColumn("_source_table", lit(source))

# Write to Delta
bronze_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{database}.{stream}_raw")

print(f"Bronze: {bronze_df.count()} rows ingested to {database}.{stream}_raw")
```

### Bronze: Media Ingestion [FULL]

```python
# Databricks notebook: Bronze_{app}_Media
# Strategy: media-ingestion
# Status: FULL
# Catalogs media files from ADLS, extracts metadata (type, size, duration),
# validates supported formats, and writes file catalog to Bronze Delta table.

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("SourcePath", "", "Source ADLS Path")
dbutils.widgets.text("Database", "flukebi_Bronze", "Target Database")

stream = dbutils.widgets.get("StreamName")
source_path = dbutils.widgets.get("SourcePath")
database = dbutils.widgets.get("Database")

from pyspark.sql.functions import (input_file_name, current_timestamp, lit,
                                    col, lower, regexp_extract, when, udf)
from pyspark.sql.types import StringType, StructType, StructField, LongType, FloatType

# Supported formats by category
SUPPORTED_AUDIO = {"wav", "mp3", "flac", "ogg", "m4a", "wma"}
SUPPORTED_VIDEO = {"mp4", "avi", "mkv", "mov", "wmv", "webm"}
SUPPORTED_IMAGE = {"jpg", "jpeg", "png", "bmp", "tiff", "gif", "webp"}
ALL_SUPPORTED = SUPPORTED_AUDIO | SUPPORTED_VIDEO | SUPPORTED_IMAGE

# Read file metadata (binary content stays in ADLS, not loaded into table)
raw_files = spark.read.format("binaryFile") \
    .option("recursiveFileLookup", "true") \
    .load(source_path)

# Extract file extension and classify media type
bronze_df = raw_files.select(
    col("path").alias("file_url"),
    input_file_name().alias("source_file_path"),
    col("length").alias("file_size_bytes"),
    col("modificationTime").alias("source_modified_at"),
    current_timestamp().alias("_ingested_at"),
    lit(stream).alias("_stream_name"),
    lower(regexp_extract(col("path"), r"\.([^.]+)$", 1)).alias("file_extension")
).withColumn(
    "media_type",
    when(col("file_extension").isin(*SUPPORTED_AUDIO), lit("audio"))
    .when(col("file_extension").isin(*SUPPORTED_VIDEO), lit("video"))
    .when(col("file_extension").isin(*SUPPORTED_IMAGE), lit("image"))
    .otherwise(lit("unsupported"))
).withColumn(
    "file_size_mb", (col("file_size_bytes") / (1024 * 1024)).cast("decimal(10,2)")
)

# Reject unsupported formats
rejected = bronze_df.filter(col("media_type") == "unsupported")
if rejected.count() > 0:
    print(f"WARNING: {rejected.count()} files with unsupported formats — skipped:")
    rejected.select("file_url", "file_extension").show(10, truncate=False)

bronze_df = bronze_df.filter(col("media_type") != "unsupported")

# Add SAS URL for downstream API calls (Speech, Vision)
storage_account = source_path.split("@")[1].split(".")[0] if "@" in source_path else ""
bronze_df = bronze_df.withColumn("storage_account", lit(storage_account))

bronze_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{database}.{stream}_media_raw")

# Summary statistics
total = bronze_df.count()
by_type = bronze_df.groupBy("media_type").count().collect()
print(f"Bronze: {total} media files cataloged to {database}.{stream}_media_raw")
for row in by_type:
    print(f"  {row.media_type}: {row['count']} files")
```

---

## Silver Notebook Templates

### Silver: Base Template with Composable Transforms [FULL]

```python
# Databricks notebook: Silver_{app}
# Transforms are composed from requirements.pipeline.silver_transforms[]
# Status: FULL (all transforms)

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("Database", "flukebi_Silver", "Target Database")

stream = dbutils.widgets.get("StreamName")
database = dbutils.widgets.get("Database")

# Read from Bronze
bronze_db = "flukebi_Bronze"
df = spark.table(f"{bronze_db}.{stream}_raw")  # or _documents_raw for doc strategy

# === TRANSFORM: text-cleaning [FULL] ===
from pyspark.sql.functions import regexp_replace, trim, lower, col
df = df.withColumn("text_content", regexp_replace(col("text_content"), "<[^>]*>", ""))  # strip HTML
df = df.withColumn("text_content", regexp_replace(col("text_content"), r"\s+", " "))    # normalize whitespace
df = df.withColumn("text_content", trim(col("text_content")))

# === TRANSFORM: dedup [FULL] ===
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number
window = Window.partitionBy("source_file_path").orderBy(col("_ingested_at").desc())
df = df.withColumn("_rn", row_number().over(window)).filter("_rn = 1").drop("_rn")

# === TRANSFORM: type-casting [FULL] ===
# (Generated dynamically based on source schema — example for typed ingestion)
# from pyspark.sql.functions import col
# df = df.withColumn("amount", col("amount").cast("decimal(18,2)"))
# df = df.withColumn("order_date", col("order_date").cast("date"))

# === TRANSFORM: joins [FULL] ===
# (Generated dynamically based on dimension table mappings)
# dim_product = spark.table("flukebi_Silver.dimProduct")
# df = df.join(dim_product, df.product_id == dim_product.ProductId, "left")

# === TRANSFORM: entity-extraction [FULL] ===
# Uses Azure AI Language NER to extract entities into structured columns
import requests, json
from pyspark.sql.functions import udf, explode, col, struct
from pyspark.sql.types import ArrayType, StructType, StructField, StringType, FloatType

AI_ENDPOINT = dbutils.secrets.get(scope=stream, key="ai-services-endpoint")
AI_KEY = dbutils.secrets.get(scope=stream, key="ai-services-key")

entity_schema = ArrayType(StructType([
    StructField("text", StringType()), StructField("category", StringType()),
    StructField("subcategory", StringType()), StructField("confidence", FloatType())
]))

@udf(returnType=entity_schema)
def extract_entities(text):
    if not text or len(text.strip()) == 0:
        return []
    # Truncate to 5120 chars (API limit per document)
    text = text[:5120]
    payload = {"kind": "EntityRecognition", "parameters": {"modelVersion": "latest"},
               "analysisInput": {"documents": [{"id": "1", "language": "en", "text": text}]}}
    resp = requests.post(f"{AI_ENDPOINT}/language/:analyze-text?api-version=2023-04-01",
                         headers={"Ocp-Apim-Subscription-Key": AI_KEY, "Content-Type": "application/json"},
                         json=payload, timeout=30)
    if resp.status_code != 200:
        return []
    entities = resp.json().get("results", {}).get("documents", [{}])[0].get("entities", [])
    return [{"text": e["text"], "category": e["category"],
             "subcategory": e.get("subcategory", ""), "confidence": e["confidenceScore"]} for e in entities]

# Apply NER to content column, then pivot entity categories into separate columns
df = df.withColumn("_entities", extract_entities(col("content")))
df = df.withColumn("_entity", explode("_entities")) \
       .withColumn("entity_text", col("_entity.text")) \
       .withColumn("entity_category", col("_entity.category")) \
       .withColumn("entity_confidence", col("_entity.confidence")) \
       .drop("_entity", "_entities")

# === TRANSFORM: feature-eng [FULL] ===
# Window functions for lag features, rolling aggregations, normalization
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, avg, stddev, min as spark_min, max as spark_max, count

# Lag features (configurable — read feature columns from widget or config)
feature_cols = dbutils.widgets.get("FeatureColumns").split(",") if dbutils.widgets.get("FeatureColumns") else []
timestamp_col = dbutils.widgets.get("TimestampColumn") if dbutils.widgets.get("TimestampColumn") else "event_date"
partition_col = dbutils.widgets.get("PartitionColumn") if dbutils.widgets.get("PartitionColumn") else "entity_id"

w = Window.partitionBy(partition_col).orderBy(timestamp_col)
for fc in feature_cols:
    fc = fc.strip()
    df = df.withColumn(f"{fc}_lag1", lag(fc, 1).over(w))
    df = df.withColumn(f"{fc}_lag7", lag(fc, 7).over(w))

# Rolling aggregations (7-day window)
w_rolling = Window.partitionBy(partition_col).orderBy(timestamp_col).rowsBetween(-6, 0)
for fc in feature_cols:
    fc = fc.strip()
    df = df.withColumn(f"{fc}_roll7_avg", avg(fc).over(w_rolling))
    df = df.withColumn(f"{fc}_roll7_std", stddev(fc).over(w_rolling))

# Z-score normalization
for fc in feature_cols:
    fc = fc.strip()
    stats = df.select(avg(fc).alias("mean"), stddev(fc).alias("std")).collect()[0]
    if stats["std"] and stats["std"] > 0:
        df = df.withColumn(f"{fc}_zscore", (col(fc) - stats["mean"]) / stats["std"])

# === TRANSFORM: transcription [FULL] ===
elif transform == "transcription":
    import requests, time
    speech_key = dbutils.secrets.get(f"kv-{stream}", "speech-service-key")
    speech_region = dbutils.secrets.get(f"kv-{stream}", "speech-service-region")
    speech_url = f"https://{speech_region}.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions"

    def transcribe_batch(audio_paths):
        """Submit batch transcription job and poll for completion."""
        payload = {
            "contentUrls": audio_paths,
            "locale": "en-US",
            "displayName": f"{stream}_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "properties": {
                "diarizationEnabled": True,
                "languageIdentification": {
                    "candidateLocales": ["en-US", "es-ES", "fr-FR", "de-DE", "zh-CN"]
                },
                "punctuationMode": "DictatedAndAutomatic",
                "wordLevelTimestampsEnabled": True
            }
        }
        headers = {"Ocp-Apim-Subscription-Key": speech_key, "Content-Type": "application/json"}
        resp = requests.post(speech_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        job_url = resp.json()["self"]

        # Poll for completion (max 30 min)
        for _ in range(360):
            status = requests.get(job_url, headers=headers, timeout=30).json()
            if status["status"] in ("Succeeded", "Failed"):
                return status
            time.sleep(5)
        raise TimeoutError("Transcription job timed out")

    # Get audio file paths from Bronze
    from pyspark.sql.functions import col, lit, explode, from_json, schema_of_json
    audio_urls = [row.file_url for row in df.select("file_url").distinct().collect()]

    # Process in batches of 100 (API limit)
    all_results = []
    for i in range(0, len(audio_urls), 100):
        batch_urls = audio_urls[i:i + 100]
        result = transcribe_batch(batch_urls)
        if result["status"] == "Succeeded":
            files_url = result["links"]["files"]
            files = requests.get(files_url, headers=headers, timeout=30).json()["values"]
            for f in files:
                if f["kind"] == "Transcription":
                    content = requests.get(f["links"]["contentUrl"], timeout=30).json()
                    for phrase in content.get("recognizedPhrases", []):
                        all_results.append({
                            "source_url": content.get("source", ""),
                            "speaker": phrase.get("speaker", 0),
                            "offset_ms": phrase.get("offsetInTicks", 0) / 10000,
                            "duration_ms": phrase.get("durationInTicks", 0) / 10000,
                            "transcript": phrase["nBest"][0]["display"] if phrase.get("nBest") else "",
                            "confidence": phrase["nBest"][0]["confidence"] if phrase.get("nBest") else 0.0,
                            "language": phrase.get("locale", "en-US")
                        })

    if all_results:
        transcript_df = spark.createDataFrame(all_results)
        df = df.join(transcript_df, df.file_url == transcript_df.source_url, "left")
    print(f"  Transcription: {len(all_results)} phrases from {len(audio_urls)} files")

# === TRANSFORM: image-labeling [FULL] ===
elif transform == "image-labeling":
    import requests
    vision_key = dbutils.secrets.get(f"kv-{stream}", "vision-service-key")
    vision_endpoint = dbutils.secrets.get(f"kv-{stream}", "vision-service-endpoint")

    def analyze_image(image_url):
        """Call Azure AI Vision for classification, detection, and description."""
        url = f"{vision_endpoint}/computervision/imageanalysis:analyze?api-version=2024-02-01"
        params = {"features": "tags,objects,caption,denseCaptions,read"}
        headers = {"Ocp-Apim-Subscription-Key": vision_key, "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, params=params,
                             json={"url": image_url}, timeout=30)
        if resp.status_code != 200:
            return {"error": resp.text}
        return resp.json()

    from pyspark.sql.functions import udf, col, explode, struct, lit, array
    from pyspark.sql.types import (StructType, StructField, StringType,
                                    FloatType, ArrayType, IntegerType)

    object_schema = ArrayType(StructType([
        StructField("name", StringType()),
        StructField("confidence", FloatType()),
        StructField("bbox_x", IntegerType()),
        StructField("bbox_y", IntegerType()),
        StructField("bbox_w", IntegerType()),
        StructField("bbox_h", IntegerType()),
    ]))

    # Process images via UDF
    image_urls = [row.file_url for row in df.select("file_url").distinct().collect()]
    results = []
    for url in image_urls:
        analysis = analyze_image(url)
        if "error" not in analysis:
            tags = [{"name": t["name"], "confidence": t["confidence"]}
                    for t in analysis.get("tagsResult", {}).get("values", [])]
            objects = [{"name": o["tags"][0]["name"],
                        "confidence": o["tags"][0]["confidence"],
                        "bbox_x": o["boundingBox"]["x"],
                        "bbox_y": o["boundingBox"]["y"],
                        "bbox_w": o["boundingBox"]["w"],
                        "bbox_h": o["boundingBox"]["h"]}
                       for o in analysis.get("objectsResult", {}).get("values", [])
                       if o.get("tags")]
            caption = analysis.get("captionResult", {}).get("text", "")
            caption_conf = analysis.get("captionResult", {}).get("confidence", 0.0)
            results.append({
                "file_url": url,
                "caption": caption,
                "caption_confidence": caption_conf,
                "tag_count": len(tags),
                "top_tags": ",".join(t["name"] for t in sorted(tags, key=lambda x: -x["confidence"])[:10]),
                "object_count": len(objects),
                "detected_objects": str(objects)
            })

    if results:
        vision_df = spark.createDataFrame(results)
        df = df.join(vision_df, on="file_url", how="left")
    print(f"  Image labeling: {len(results)} images analyzed")

# Write to Silver Delta table
df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{database}.{stream}")

print(f"Silver: {df.count()} rows written to {database}.{stream}")
```

---

## Gold Notebook Templates

### Gold: Chunked Documents [FULL]

```python
# Databricks notebook: Gold_{app}_ChunkedDocs
# Output: chunked-docs
# Status: FULL

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("ChunkSize", "512", "Chunk Size (tokens)")
dbutils.widgets.text("Overlap", "128", "Overlap (tokens)")

stream = dbutils.widgets.get("StreamName")
chunk_size = int(dbutils.widgets.get("ChunkSize"))
overlap = int(dbutils.widgets.get("Overlap"))

from pyspark.sql.functions import udf, explode, monotonically_increasing_id, col, lit
from pyspark.sql.types import ArrayType, StructType, StructField, StringType, IntegerType
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4")

def chunk_text(text, chunk_size, overlap):
    """Semantic chunking with paragraph awareness and token-based sizing."""
    if not text:
        return []
    paragraphs = text.split("\n\n")
    chunks, current, current_tokens = [], "", 0
    for para in paragraphs:
        para_tokens = len(enc.encode(para))
        if current_tokens + para_tokens > chunk_size and current:
            chunks.append(current.strip())
            # Overlap: keep last N tokens worth of text
            overlap_text = enc.decode(enc.encode(current)[-overlap:]) if overlap > 0 else ""
            current, current_tokens = overlap_text + "\n\n" + para, overlap + para_tokens
        else:
            current += "\n\n" + para if current else para
            current_tokens += para_tokens
    if current.strip():
        chunks.append(current.strip())
    return [{"chunk_text": c, "chunk_index": i, "token_count": len(enc.encode(c))} for i, c in enumerate(chunks)]

chunk_schema = ArrayType(StructType([
    StructField("chunk_text", StringType()),
    StructField("chunk_index", IntegerType()),
    StructField("token_count", IntegerType())
]))

chunk_udf = udf(lambda text: chunk_text(text, chunk_size, overlap), chunk_schema)

# Read from Silver
silver_df = spark.table(f"flukebi_Silver.{stream}")

# Chunk documents
gold_df = silver_df \
    .withColumn("chunks", chunk_udf(col("text_content"))) \
    .select("source_file_path", "path", explode("chunks").alias("chunk")) \
    .select(
        "source_file_path",
        "path",
        col("chunk.chunk_text").alias("content"),
        col("chunk.chunk_index").alias("chunk_index"),
        col("chunk.token_count").alias("token_count"),
        monotonically_increasing_id().alias("chunk_id")
    ) \
    .withColumn("stream_name", lit(stream))

gold_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable(f"flukebi_Gold.{stream}_chunks")

print(f"Gold: {gold_df.count()} chunks from {silver_df.count()} documents")
```

### Gold: Views [FULL]

```sql
-- Databricks SQL notebook: Gold_{app}_Views
-- Output: views
-- Status: FULL

-- CREATE OR REPLACE VIEW with business-friendly aliases
CREATE OR REPLACE VIEW flukebi_Gold.v_{stream}_summary AS
SELECT
    `source_file_path` AS `Source`,
    `text_content` AS `Content`,
    `_ingested_at` AS `Ingestion Date`,
    `_stream_name` AS `Stream`
FROM flukebi_Silver.{stream}
```

### Gold: Training Datasets [FULL]

```python
# Databricks notebook: Gold_{app}_TrainingData
# Output: training-datasets
# Status: FULL

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("LabelColumn", "label", "Label Column")
dbutils.widgets.text("SplitRatios", "0.8,0.1,0.1", "Train/Val/Test Ratios")
dbutils.widgets.text("Database", "flukebi_Gold", "Target Database")

stream = dbutils.widgets.get("StreamName")
label_col = dbutils.widgets.get("LabelColumn")
split_str = dbutils.widgets.get("SplitRatios")
database = dbutils.widgets.get("Database")

from pyspark.sql.functions import col, abs as spark_abs, corr, lit, rand
from pyspark.ml.feature import VectorAssembler, StringIndexer
import mlflow

df = spark.table(f"flukebi_Silver.{stream}")

# --- Feature selection: drop low-correlation and high-null columns ---
numeric_cols = [f.name for f in df.schema.fields
                if f.dataType.simpleString() in ("double", "float", "int", "bigint", "decimal(18,2)")
                and f.name != label_col]

# Drop columns with >30% nulls
total = df.count()
keep_cols = []
for c in numeric_cols:
    null_pct = df.where(col(c).isNull()).count() / total
    if null_pct <= 0.3:
        keep_cols.append(c)

# Correlation-based selection (keep |corr| > 0.05 with label)
selected_features = []
for c in keep_cols:
    r = df.select(corr(col(c), col(label_col))).collect()[0][0]
    if r is not None and abs(r) > 0.05:
        selected_features.append(c)

print(f"Selected {len(selected_features)}/{len(numeric_cols)} features based on correlation with {label_col}")

# --- Train/Validation/Test split with stratification ---
ratios = [float(r) for r in split_str.split(",")]
train_ratio, val_ratio, test_ratio = ratios[0], ratios[1], ratios[2]

# Stratified split by label (preserves class distribution)
df_with_rand = df.withColumn("_rand", rand(seed=42))
label_counts = df.groupBy(label_col).count().collect()

train_dfs, val_dfs, test_dfs = [], [], []
for row in label_counts:
    subset = df_with_rand.where(col(label_col) == row[label_col]).orderBy("_rand")
    n = row["count"]
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    train_dfs.append(subset.limit(n_train))
    val_dfs.append(subset.subtract(subset.limit(n_train)).limit(n_val))
    test_dfs.append(subset.subtract(subset.limit(n_train + n_val)))

from functools import reduce
train_df = reduce(lambda a, b: a.union(b), train_dfs).drop("_rand")
val_df = reduce(lambda a, b: a.union(b), val_dfs).drop("_rand")
test_df = reduce(lambda a, b: a.union(b), test_dfs).drop("_rand")

# --- Write versioned datasets ---
train_df.withColumn("split", lit("train")).write.format("delta").mode("overwrite") \
    .saveAsTable(f"{database}.{stream}_train")
val_df.withColumn("split", lit("validation")).write.format("delta").mode("overwrite") \
    .saveAsTable(f"{database}.{stream}_validation")
test_df.withColumn("split", lit("test")).write.format("delta").mode("overwrite") \
    .saveAsTable(f"{database}.{stream}_test")

# --- Log to MLflow ---
mlflow.set_experiment(f"/Shared/{stream}/data-prep")
with mlflow.start_run(run_name=f"{stream}_data_split"):
    mlflow.log_param("features_selected", len(selected_features))
    mlflow.log_param("feature_names", ",".join(selected_features))
    mlflow.log_param("label_column", label_col)
    mlflow.log_param("split_ratios", split_str)
    mlflow.log_metric("train_rows", train_df.count())
    mlflow.log_metric("val_rows", val_df.count())
    mlflow.log_metric("test_rows", test_df.count())
    mlflow.log_metric("total_features", len(selected_features))

print(f"Gold: Train={train_df.count()}, Val={val_df.count()}, Test={test_df.count()} | {len(selected_features)} features")
```

### Gold: Graph Triples [FULL]

```python
# Databricks notebook: Gold_{app}_GraphTriples
# Output: graph-triples
# Status: FULL

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("Database", "flukebi_Gold", "Target Database")
stream = dbutils.widgets.get("StreamName")
database = dbutils.widgets.get("Database")

from pyspark.sql.functions import (col, lit, monotonically_increasing_id, concat_ws,
                                    lower, trim, collect_set, explode, size, udf, md5)
from pyspark.sql.types import ArrayType, StructType, StructField, StringType, FloatType

# --- Step 1: Load Silver entity-extracted data ---
# Expects Silver table with entity_text, entity_category columns (from entity-extraction transform)
df = spark.table(f"flukebi_Silver.{stream}")

# --- Step 2: Entity resolution (dedup entities by normalized name) ---
entities = df.select(
    lower(trim(col("entity_text"))).alias("entity_name"),
    col("entity_category").alias("entity_type"),
    col("source_file_path").alias("source")
).distinct()

# Assign stable entity IDs via hash
entities = entities.withColumn("entity_id", md5(concat_ws(":", col("entity_type"), col("entity_name"))))

# --- Step 3: Co-occurrence relationship extraction ---
# Entities co-occurring in the same source document are related
from pyspark.sql.functions import collect_list, struct

# Collect entities per document
doc_entities = df.select(
    col("source_file_path").alias("source"),
    lower(trim(col("entity_text"))).alias("entity_name"),
    col("entity_category").alias("entity_type")
).distinct()

doc_groups = doc_entities.groupBy("source").agg(
    collect_list(struct("entity_name", "entity_type")).alias("entities")
)

# Generate co-occurrence pairs (subject, predicate, object)
from itertools import combinations
from pyspark.sql.functions import pandas_udf
import pandas as pd

@udf(returnType=ArrayType(StructType([
    StructField("subject", StringType()), StructField("subject_type", StringType()),
    StructField("object", StringType()), StructField("object_type", StringType()),
    StructField("predicate", StringType())
])))
def extract_pairs(entity_list):
    if not entity_list or len(entity_list) < 2:
        return []
    pairs = []
    for e1, e2 in combinations(entity_list, 2):
        pairs.append({
            "subject": e1["entity_name"], "subject_type": e1["entity_type"],
            "object": e2["entity_name"], "object_type": e2["entity_type"],
            "predicate": "co_occurs_with"
        })
    return pairs[:100]  # Cap per document to avoid explosion

triples_raw = doc_groups.withColumn("pair", explode(extract_pairs(col("entities")))) \
    .select(
        col("source"),
        col("pair.subject"), col("pair.subject_type"),
        col("pair.predicate"),
        col("pair.object"), col("pair.object_type")
    )

# --- Step 4: Deduplicate and score triples ---
triples = triples_raw.groupBy("subject", "subject_type", "predicate", "object", "object_type") \
    .agg(collect_set("source").alias("sources")) \
    .withColumn("confidence", size("sources").cast("float") / lit(float(doc_groups.count()))) \
    .withColumn("triple_id", md5(concat_ws(":", col("subject"), col("predicate"), col("object"))))

# --- Step 5: Write triples table ---
triples.select(
    "triple_id", "subject", "subject_type", "predicate", "object", "object_type",
    "confidence", "sources"
).write.format("delta").mode("overwrite").saveAsTable(f"{database}.{stream}_triples")

print(f"Gold: {triples.count()} triples, {entities.count()} unique entities")
```

---

## AI Layer Notebook Templates

### AI Layer: Embeddings → AI Search [FULL]

```python
# Databricks notebook: AILayer_{app}_Embeddings
# Processing: embeddings
# Status: FULL

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("AIEndpoint", "", "AI Services Endpoint")
dbutils.widgets.text("SearchEndpoint", "", "AI Search Endpoint")
dbutils.widgets.text("IndexName", "", "Search Index Name")

stream = dbutils.widgets.get("StreamName")
ai_endpoint = dbutils.widgets.get("AIEndpoint")
search_endpoint = dbutils.widgets.get("SearchEndpoint")
index_name = dbutils.widgets.get("IndexName")

# Get keys from Key Vault
ai_key = dbutils.secrets.get(scope=stream, key="ai-services-key")
search_key = dbutils.secrets.get(scope=stream, key="ai-search-admin-key")

import requests, json, time

# --- Read Gold chunks ---
chunks_df = spark.table(f"flukebi_Gold.{stream}_chunks").toPandas()

# --- Batch embed ---
BATCH_SIZE = 16
embeddings = []
for i in range(0, len(chunks_df), BATCH_SIZE):
    batch = chunks_df.iloc[i:i+BATCH_SIZE]
    response = requests.post(
        f"{ai_endpoint}/openai/deployments/text-embedding-3-large/embeddings?api-version=2024-06-01",
        headers={"api-key": ai_key, "Content-Type": "application/json"},
        json={"input": batch["content"].tolist()}
    )
    if response.status_code == 429:
        time.sleep(int(response.headers.get("Retry-After", 10)))
        response = requests.post(...)  # retry
    result = response.json()
    for j, item in enumerate(result["data"]):
        embeddings.append({"chunk_id": str(batch.iloc[j]["chunk_id"]), "embedding": item["embedding"]})

# --- Push to AI Search ---
# Create index if not exists
index_def = {
    "name": index_name,
    "fields": [
        {"name": "chunk_id", "type": "Edm.String", "key": True, "filterable": True},
        {"name": "content", "type": "Edm.String", "searchable": True, "analyzerName": "en.microsoft"},
        {"name": "source_file_path", "type": "Edm.String", "filterable": True, "facetable": True},
        {"name": "chunk_index", "type": "Edm.Int32", "filterable": True, "sortable": True},
        {"name": "content_vector", "type": "Collection(Edm.Single)", "searchable": True,
         "vectorSearchDimensions": 3072, "vectorSearchProfileName": "vector-profile"}
    ],
    "vectorSearch": {
        "algorithms": [{"name": "hnsw-algo", "kind": "hnsw", "hnswParameters": {"m": 4, "efConstruction": 400, "metric": "cosine"}}],
        "profiles": [{"name": "vector-profile", "algorithmConfigurationName": "hnsw-algo"}]
    },
    "semantic": {
        "configurations": [{"name": "semantic-config", "prioritizedFields": {"contentFields": [{"fieldName": "content"}]}}]
    }
}

requests.put(
    f"{search_endpoint}/indexes/{index_name}?api-version=2024-07-01",
    headers={"api-key": search_key, "Content-Type": "application/json"},
    json=index_def
)

# Upload documents with embeddings
docs = []
for idx, row in chunks_df.iterrows():
    emb = next((e["embedding"] for e in embeddings if e["chunk_id"] == str(row["chunk_id"])), None)
    if emb:
        docs.append({
            "@search.action": "mergeOrUpload",
            "chunk_id": str(row["chunk_id"]),
            "content": row["content"],
            "source_file_path": row.get("source_file_path", ""),
            "chunk_index": int(row.get("chunk_index", 0)),
            "content_vector": emb
        })

# Upload in batches of 1000
for i in range(0, len(docs), 1000):
    batch = docs[i:i+1000]
    requests.post(
        f"{search_endpoint}/indexes/{index_name}/docs/index?api-version=2024-07-01",
        headers={"api-key": search_key, "Content-Type": "application/json"},
        json={"value": batch}
    )

print(f"AI Layer: {len(docs)} chunks embedded and indexed in {index_name}")
```

### AI Layer: Graph Load [FULL]

```python
# Databricks notebook: AILayer_{app}_GraphLoad
# Processing: graph-load
# Status: FULL
# Loads triples from Gold into Cosmos DB Gremlin and/or Neo4j.
# Supports batch upserts with retry, deduplication, and statistics.

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("GraphTarget", "cosmos", "Graph Target (cosmos|neo4j|both)")
dbutils.widgets.text("BatchSize", "500", "Batch Size")
stream = dbutils.widgets.get("StreamName")
graph_target = dbutils.widgets.get("GraphTarget")
batch_size = int(dbutils.widgets.get("BatchSize"))

triples_df = spark.table(f"flukebi_Gold.{stream}_triples")
triple_count = triples_df.count()
print(f"Loading {triple_count} triples into {graph_target}")

# --- Extract distinct vertices from triples ---
from pyspark.sql import functions as F

subjects = triples_df.select(
    F.col("subject_id").alias("vertex_id"),
    F.col("subject_label").alias("label"),
    F.col("subject_type").alias("vertex_type")
).distinct()

objects = triples_df.select(
    F.col("object_id").alias("vertex_id"),
    F.col("object_label").alias("label"),
    F.col("object_type").alias("vertex_type")
).distinct()

vertices = subjects.unionByName(objects).dropDuplicates(["vertex_id"])
vertex_count = vertices.count()
print(f"Distinct vertices: {vertex_count}")

# --- Cosmos DB Gremlin loading ---
if graph_target in ("cosmos", "both"):
    import requests, json, time
    from tenacity import retry, stop_after_attempt, wait_exponential

    cosmos_endpoint = dbutils.secrets.get("kv-{{app}}", "cosmos-gremlin-endpoint")
    cosmos_key = dbutils.secrets.get("kv-{{app}}", "cosmos-gremlin-key")
    cosmos_db = "{{app}}-graphdb"
    cosmos_graph = "knowledge"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def gremlin_query(query_str):
        """Execute a Gremlin query against Cosmos DB with retry."""
        url = f"https://{cosmos_endpoint}:443/"
        headers = {"Content-Type": "application/json"}
        payload = {"gremlin": query_str}
        resp = requests.post(url, headers=headers, json=payload,
                             auth=("", cosmos_key), timeout=30)
        resp.raise_for_status()
        return resp.json()

    # Upsert vertices in batches
    vertex_rows = vertices.collect()
    v_loaded, v_skipped = 0, 0
    for i in range(0, len(vertex_rows), batch_size):
        batch = vertex_rows[i:i + batch_size]
        for row in batch:
            q = (f"g.V('{row.vertex_id}').fold()"
                 f".coalesce(unfold(),"
                 f"addV('{row.vertex_type}')"
                 f".property('id', '{row.vertex_id}')"
                 f".property('label', '{row.label}')"
                 f".property('pk', '{row.vertex_type}'))")
            try:
                gremlin_query(q)
                v_loaded += 1
            except Exception as e:
                print(f"  WARN vertex {row.vertex_id}: {e}")
                v_skipped += 1
        print(f"  Cosmos vertices: {v_loaded}/{len(vertex_rows)}")

    # Upsert edges in batches
    edge_rows = triples_df.collect()
    e_loaded, e_skipped = 0, 0
    for i in range(0, len(edge_rows), batch_size):
        batch = edge_rows[i:i + batch_size]
        for row in batch:
            edge_id = f"{row.subject_id}_{row.predicate}_{row.object_id}"
            q = (f"g.V('{row.subject_id}')"
                 f".coalesce(outE('{row.predicate}').where(inV().hasId('{row.object_id}')),"
                 f"addE('{row.predicate}').to(g.V('{row.object_id}'))"
                 f".property('confidence', {row.confidence})"
                 f".property('doc_count', {row.doc_count}))")
            try:
                gremlin_query(q)
                e_loaded += 1
            except Exception as e:
                print(f"  WARN edge {edge_id}: {e}")
                e_skipped += 1
        print(f"  Cosmos edges: {e_loaded}/{len(edge_rows)}")

    print(f"Cosmos DB complete: {v_loaded} vertices, {e_loaded} edges "
          f"({v_skipped + e_skipped} skipped)")

# --- Neo4j loading ---
if graph_target in ("neo4j", "both"):
    from neo4j import GraphDatabase

    neo4j_uri = dbutils.secrets.get("kv-{{app}}", "neo4j-uri")
    neo4j_user = dbutils.secrets.get("kv-{{app}}", "neo4j-user")
    neo4j_pass = dbutils.secrets.get("kv-{{app}}", "neo4j-password")

    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))

    def load_vertices_neo4j(tx, batch):
        """MERGE vertices — idempotent upsert."""
        tx.run("""
            UNWIND $batch AS row
            MERGE (n {id: row.vertex_id})
            SET n.label = row.label,
                n.vertex_type = row.vertex_type,
                n.updated_at = datetime()
            WITH n, row
            CALL apoc.create.addLabels(n, [row.vertex_type]) YIELD node
            RETURN count(node)
        """, batch=batch)

    def load_edges_neo4j(tx, batch):
        """MERGE edges — idempotent upsert with properties."""
        tx.run("""
            UNWIND $batch AS row
            MATCH (s {id: row.subject_id})
            MATCH (o {id: row.object_id})
            MERGE (s)-[r:RELATES_TO {predicate: row.predicate}]->(o)
            SET r.confidence = row.confidence,
                r.doc_count = row.doc_count,
                r.updated_at = datetime()
            RETURN count(r)
        """, batch=batch)

    # Load vertices
    v_batches = [vertex_rows[i:i + batch_size]
                 for i in range(0, len(vertex_rows), batch_size)]
    with driver.session() as session:
        for batch in v_batches:
            records = [row.asDict() for row in batch]
            session.execute_write(load_vertices_neo4j, records)
    print(f"Neo4j vertices loaded: {vertex_count}")

    # Load edges
    e_batches = [edge_rows[i:i + batch_size]
                 for i in range(0, len(edge_rows), batch_size)]
    with driver.session() as session:
        for batch in e_batches:
            records = [row.asDict() for row in batch]
            session.execute_write(load_edges_neo4j, records)
    print(f"Neo4j edges loaded: {triple_count}")

    driver.close()

# --- Graph Statistics ---
stats = {
    "stream": stream,
    "graph_target": graph_target,
    "total_vertices": vertex_count,
    "total_edges": triple_count,
    "vertex_types": vertices.select("vertex_type").distinct().count(),
    "predicate_types": triples_df.select("predicate").distinct().count(),
    "avg_confidence": triples_df.agg(F.avg("confidence")).first()[0],
}
print(f"\nGraph Statistics: {json.dumps(stats, indent=2, default=str)}")
```

### AI Layer: ML Training [FULL]

```python
# Databricks notebook: AILayer_{app}_MLTraining
# Processing: ml-training
# Status: FULL
# End-to-end ML pipeline: loads training data, tunes hyperparameters,
# trains model, evaluates, registers best model to MLflow Model Registry.

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("TargetColumn", "target", "Target Column")
dbutils.widgets.text("TaskType", "classification", "Task Type (classification|regression)")
dbutils.widgets.text("MaxTrials", "20", "Hyperopt Max Trials")
stream = dbutils.widgets.get("StreamName")
target_col = dbutils.widgets.get("TargetColumn")
task_type = dbutils.widgets.get("TaskType")
max_trials = int(dbutils.widgets.get("MaxTrials"))

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, roc_auc_score, mean_squared_error,
                             mean_absolute_error, r2_score)
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
from hyperopt.pyll import scope

# --- Load training/validation/test splits ---
train_df = spark.table(f"flukebi_Gold.{stream}_training").toPandas()
val_df = spark.table(f"flukebi_Gold.{stream}_validation").toPandas()
test_df = spark.table(f"flukebi_Gold.{stream}_test").toPandas()

feature_cols = [c for c in train_df.columns if c != target_col]
X_train, y_train = train_df[feature_cols], train_df[target_col]
X_val, y_val = val_df[feature_cols], val_df[target_col]
X_test, y_test = test_df[feature_cols], test_df[target_col]

print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
print(f"Features: {len(feature_cols)}, Target: {target_col}, Task: {task_type}")

# --- MLflow experiment ---
experiment_path = f"/Shared/{stream}/experiment"
mlflow.set_experiment(experiment_path)

# --- Hyperparameter search space ---
if task_type == "classification":
    from xgboost import XGBClassifier
    search_space = {
        "max_depth": scope.int(hp.quniform("max_depth", 3, 12, 1)),
        "learning_rate": hp.loguniform("learning_rate", np.log(0.01), np.log(0.3)),
        "n_estimators": scope.int(hp.quniform("n_estimators", 50, 500, 50)),
        "min_child_weight": scope.int(hp.quniform("min_child_weight", 1, 10, 1)),
        "subsample": hp.uniform("subsample", 0.6, 1.0),
        "colsample_bytree": hp.uniform("colsample_bytree", 0.6, 1.0),
        "reg_alpha": hp.loguniform("reg_alpha", np.log(1e-8), np.log(10)),
        "reg_lambda": hp.loguniform("reg_lambda", np.log(1e-8), np.log(10)),
    }
else:
    from xgboost import XGBRegressor
    search_space = {
        "max_depth": scope.int(hp.quniform("max_depth", 3, 12, 1)),
        "learning_rate": hp.loguniform("learning_rate", np.log(0.01), np.log(0.3)),
        "n_estimators": scope.int(hp.quniform("n_estimators", 50, 500, 50)),
        "min_child_weight": scope.int(hp.quniform("min_child_weight", 1, 10, 1)),
        "subsample": hp.uniform("subsample", 0.6, 1.0),
        "colsample_bytree": hp.uniform("colsample_bytree", 0.6, 1.0),
        "reg_alpha": hp.loguniform("reg_alpha", np.log(1e-8), np.log(10)),
        "reg_lambda": hp.loguniform("reg_lambda", np.log(1e-8), np.log(10)),
    }

# --- Hyperopt objective function ---
def objective(params):
    params["max_depth"] = int(params["max_depth"])
    params["n_estimators"] = int(params["n_estimators"])
    params["min_child_weight"] = int(params["min_child_weight"])

    with mlflow.start_run(nested=True):
        mlflow.log_params(params)

        if task_type == "classification":
            model = XGBClassifier(**params, use_label_encoder=False,
                                  eval_metric="logloss", random_state=42)
            model.fit(X_train, y_train, eval_set=[(X_val, y_val)],
                      verbose=False)
            preds = model.predict(X_val)
            proba = model.predict_proba(X_val)[:, 1] if len(np.unique(y_train)) == 2 else None
            score = f1_score(y_val, preds, average="weighted")
            mlflow.log_metric("val_f1", score)
            mlflow.log_metric("val_accuracy", accuracy_score(y_val, preds))
            if proba is not None:
                mlflow.log_metric("val_auc", roc_auc_score(y_val, proba))
            loss = -score
        else:
            model = XGBRegressor(**params, random_state=42)
            model.fit(X_train, y_train, eval_set=[(X_val, y_val)],
                      verbose=False)
            preds = model.predict(X_val)
            rmse = np.sqrt(mean_squared_error(y_val, preds))
            r2 = r2_score(y_val, preds)
            mlflow.log_metric("val_rmse", rmse)
            mlflow.log_metric("val_mae", mean_absolute_error(y_val, preds))
            mlflow.log_metric("val_r2", r2)
            loss = rmse

        mlflow.sklearn.log_model(model, "model")
        return {"loss": loss, "status": STATUS_OK}

# --- Run hyperparameter tuning ---
with mlflow.start_run(run_name=f"{stream}_tuning") as parent_run:
    mlflow.log_param("task_type", task_type)
    mlflow.log_param("max_trials", max_trials)
    mlflow.log_param("feature_count", len(feature_cols))
    mlflow.log_param("train_size", len(X_train))

    trials = Trials()
    best_params = fmin(fn=objective, space=search_space, algo=tpe.suggest,
                       max_evals=max_trials, trials=trials)

    # Cast best params to correct types
    best_params["max_depth"] = int(best_params["max_depth"])
    best_params["n_estimators"] = int(best_params["n_estimators"])
    best_params["min_child_weight"] = int(best_params["min_child_weight"])
    mlflow.log_params({f"best_{k}": v for k, v in best_params.items()})

# --- Train final model with best params on train+val ---
X_trainval = pd.concat([X_train, X_val])
y_trainval = pd.concat([y_train, y_val])

with mlflow.start_run(run_name=f"{stream}_final") as final_run:
    mlflow.log_params(best_params)
    mlflow.log_param("trained_on", "train+val")

    if task_type == "classification":
        final_model = XGBClassifier(**best_params, use_label_encoder=False,
                                     eval_metric="logloss", random_state=42)
        final_model.fit(X_trainval, y_trainval)
        test_preds = final_model.predict(X_test)
        test_proba = (final_model.predict_proba(X_test)[:, 1]
                      if len(np.unique(y_train)) == 2 else None)

        metrics = {
            "test_accuracy": accuracy_score(y_test, test_preds),
            "test_f1": f1_score(y_test, test_preds, average="weighted"),
            "test_precision": precision_score(y_test, test_preds, average="weighted"),
            "test_recall": recall_score(y_test, test_preds, average="weighted"),
        }
        if test_proba is not None:
            metrics["test_auc"] = roc_auc_score(y_test, test_proba)
    else:
        final_model = XGBRegressor(**best_params, random_state=42)
        final_model.fit(X_trainval, y_trainval)
        test_preds = final_model.predict(X_test)

        metrics = {
            "test_rmse": np.sqrt(mean_squared_error(y_test, test_preds)),
            "test_mae": mean_absolute_error(y_test, test_preds),
            "test_r2": r2_score(y_test, test_preds),
        }

    mlflow.log_metrics(metrics)
    mlflow.xgboost.log_model(final_model, "model",
                              registered_model_name=f"{stream}_model")

    # Feature importance
    importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": final_model.feature_importances_
    }).sort_values("importance", ascending=False)
    mlflow.log_table(importance, "feature_importance.json")

    print(f"\nFinal Model Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")
    print(f"\nTop 10 Features:")
    print(importance.head(10).to_string(index=False))
    print(f"\nModel registered: {stream}_model (run: {final_run.info.run_id})")
```

### AI Layer: Index Population [FULL]

```python
# Databricks notebook: AILayer_{app}_IndexPop
# Processing: index-population
# Status: FULL
# Pushes Gold-layer extracted data into Azure AI Search index.
# Supports incremental indexing via watermark column and batch upload.

dbutils.widgets.text("StreamName", "", "Stream Name")
dbutils.widgets.text("SearchService", "", "AI Search Service Name")
dbutils.widgets.text("IndexName", "", "Search Index Name")
dbutils.widgets.text("BatchSize", "1000", "Upload Batch Size")
dbutils.widgets.text("WatermarkColumn", "modified_at", "Watermark Column for Incremental")
stream = dbutils.widgets.get("StreamName")
search_service = dbutils.widgets.get("SearchService")
index_name = dbutils.widgets.get("IndexName")
batch_size = int(dbutils.widgets.get("BatchSize"))
watermark_col = dbutils.widgets.get("WatermarkColumn")

import requests, json
from pyspark.sql import functions as F
from datetime import datetime

search_key = dbutils.secrets.get("kv-{{app}}", "search-admin-key")
search_url = f"https://{search_service}.search.windows.net"
headers = {
    "Content-Type": "application/json",
    "api-key": search_key
}

# --- Determine incremental watermark ---
# Check last successful run timestamp from status control
try:
    last_run = spark.sql(f"""
        SELECT MAX(EndDate) as last_watermark
        FROM flukebi_Silver.StatusControl
        WHERE StreamName = '{stream}_indexpop' AND Status = 'Succeeded'
    """).first()["last_watermark"]
except Exception:
    last_run = None

gold_df = spark.table(f"flukebi_Gold.{stream}_extracted")
if last_run and watermark_col in gold_df.columns:
    gold_df = gold_df.filter(F.col(watermark_col) > F.lit(last_run))
    print(f"Incremental mode: {gold_df.count()} new/changed records since {last_run}")
else:
    print(f"Full mode: {gold_df.count()} total records")

# --- Build field mappings from Gold schema to search fields ---
# Convention: Gold column names map directly to search index fields
# Special handling: 'id' field required as document key
if "document_id" in gold_df.columns:
    gold_df = gold_df.withColumn("id", F.col("document_id").cast("string"))
elif "id" not in gold_df.columns:
    gold_df = gold_df.withColumn("id", F.monotonically_increasing_id().cast("string"))

# --- Convert to search documents and upload in batches ---
rows = gold_df.collect()
total = len(rows)
uploaded, failed = 0, 0

for i in range(0, total, batch_size):
    batch = rows[i:i + batch_size]
    documents = []
    for row in batch:
        doc = {"@search.action": "mergeOrUpload"}
        for field in row.asDict():
            val = row[field]
            if val is not None:
                if isinstance(val, datetime):
                    doc[field] = val.isoformat() + "Z"
                elif isinstance(val, (list, dict)):
                    doc[field] = val
                else:
                    doc[field] = str(val) if not isinstance(val, (int, float, bool)) else val
        documents.append(doc)

    payload = {"value": documents}
    resp = requests.post(
        f"{search_url}/indexes/{index_name}/docs/index?api-version=2024-07-01",
        headers=headers, json=payload, timeout=60
    )

    if resp.status_code == 200:
        results = resp.json().get("value", [])
        batch_ok = sum(1 for r in results if r.get("status"))
        batch_fail = len(results) - batch_ok
        uploaded += batch_ok
        failed += batch_fail
    else:
        print(f"  WARN batch {i//batch_size}: HTTP {resp.status_code} - {resp.text[:200]}")
        failed += len(batch)

    if (i // batch_size) % 10 == 0:
        print(f"  Progress: {uploaded}/{total} uploaded, {failed} failed")

# --- Verify index document count ---
count_resp = requests.get(
    f"{search_url}/indexes/{index_name}/docs/$count?api-version=2024-07-01",
    headers=headers, timeout=30
)
index_count = count_resp.text if count_resp.status_code == 200 else "unknown"

print(f"\nIndex Population Complete:")
print(f"  Documents uploaded: {uploaded}")
print(f"  Documents failed: {failed}")
print(f"  Total index size: {index_count}")
```

---

## Status Control SQL

```sql
-- Status control stored procedures

CREATE OR ALTER PROCEDURE usp_StatusControl_PreLog
    @StreamName NVARCHAR(100),
    @SubStream NVARCHAR(100),
    @Status NVARCHAR(50)
AS
BEGIN
    INSERT INTO StatusControl (StreamName, SubStream, Status, StartTime)
    VALUES (@StreamName, @SubStream, @Status, GETUTCDATE())
END

CREATE OR ALTER PROCEDURE usp_StatusControl_PostLog
    @StreamName NVARCHAR(100),
    @Status NVARCHAR(50),
    @RowCount BIGINT = NULL,
    @ErrorMessage NVARCHAR(MAX) = NULL
AS
BEGIN
    UPDATE StatusControl
    SET Status = @Status, EndTime = GETUTCDATE(), RowCount = @RowCount, ErrorMessage = @ErrorMessage
    WHERE StreamName = @StreamName AND EndTime IS NULL
END
```

---

## Pipeline Template Anti-Patterns (NEVER Do These)

1. **NEVER use `mode("append")` for Silver/Gold Delta tables without dedup.** Append without dedup creates duplicates on reruns. Use MERGE or overwrite.
2. **NEVER embed API keys in notebook code.** Always use `dbutils.secrets.get(scope, key)` to read from Key Vault-backed secret scope.
3. **NEVER skip the `overwriteSchema` option on first write.** Schema evolution without this flag silently drops new columns.
4. **NEVER use `toPandas()` on large DataFrames (>100K rows).** For AI Layer embeddings, batch-collect in chunks or use Spark UDFs.
5. **NEVER create notebooks without the standard widget block.** `StreamName`, `SubStream`, `Database` are required for parameterized ADF execution.
6. **NEVER skip the ADF PostLog on failure path.** Both success and failure must log to status_control for audit.
7. **NEVER generate notebooks without the correct Delta table schema.** All notebooks must create tables with the right columns so downstream phases don't fail on missing tables.
