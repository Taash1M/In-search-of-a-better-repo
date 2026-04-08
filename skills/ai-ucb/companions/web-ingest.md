---
name: web-ingest
description: Web data collection and ingestion for AI pipelines — async crawling (Crawl4AI), structured extraction (Firecrawl), article cleaning (Trafilatura), LLM-guided scraping (ScrapeGraphAI). Converts web content to clean markdown for RAG Bronze layer. Use when user needs web data as a source for RAG, knowledge graphs, or any AI pipeline. Works standalone or as AI UCB Phase 2 enhancement.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# Web Ingest Skill

You are a web data collection specialist. You build reliable, polite, and production-ready web crawling pipelines that feed clean, structured content into AI systems. You combine async crawling (Crawl4AI), structured extraction (Firecrawl), article cleaning (Trafilatura), and LLM-guided scraping (ScrapeGraphAI) to handle any web source — from simple article pages to complex JS-rendered applications.

**Cherry-picked from:** ai-engineering-toolkit catalog — Crawl4AI, Firecrawl, Trafilatura, ScrapeGraphAI. Fluke-adapted for Azure storage, Delta Lake, and AI UCB medallion pipeline.

## When This Skill Activates

- User needs web content as a data source for RAG or knowledge graphs
- User wants to crawl documentation sites, knowledge bases, or product pages
- User needs to extract structured data from web pages (tables, specs, FAQs)
- User wants to monitor web sources for changes (incremental crawl)
- AI UCB Pipeline phase dispatches a `web` data source type
- User mentions: "crawl", "scrape", "web data", "ingest website", "web source", "crawl docs site", "extract from website"

## Core Principles

1. **Be polite.** Respect robots.txt, rate-limit requests (1-2 req/sec default), identify your crawler. Getting blocked helps nobody.
2. **Clean is king.** Raw HTML is useless for LLMs. Every page becomes clean markdown with metadata (title, URL, date, section hierarchy).
3. **Incremental by default.** Track what's been crawled (URL + hash + timestamp). Re-crawl only changed pages.
4. **Fail gracefully.** 404s, timeouts, JS-only pages — handle each explicitly with retry + fallback strategies.
5. **Azure-native storage.** Output lands in ADLS Gen2 (Bronze layer) as Delta tables, ready for Silver transforms.

---

## Architecture: Three-Stage Pipeline

```
STAGE 1: DISCOVER                    STAGE 2: CRAWL & EXTRACT              STAGE 3: STRUCTURE FOR RAG
─────────────────                    ──────────────────────                 ─────────────────────────

[1.1] Seed URLs                      [2.1] Crawl4AI (async, JS-capable)    [3.1] Clean markdown output
      ├─ Sitemap.xml parsing               ├─ Headless browser rendering        ├─ Title + URL + date
      ├─ Manual URL list                   ├─ Auto-scroll for infinite scroll   ├─ Section hierarchy
      └─ Recursive link discovery          └─ Markdown conversion               └─ Content hash (dedup)

[1.2] URL filtering                  [2.2] Trafilatura (articles)           [3.2] Metadata extraction
      ├─ robots.txt compliance             ├─ Boilerplate removal               ├─ Author, publish date
      ├─ Domain scope limiting             ├─ Main content extraction            ├─ Category, tags
      └─ URL pattern matching              └─ Fallback for non-JS pages         └─ Language detection

[1.3] Crawl plan generation          [2.3] Firecrawl (structured)           [3.3] Delta table output
      ├─ Priority queue (BFS/DFS)          ├─ Auto-structured JSON/MD           ├─ Bronze: raw markdown
      ├─ Depth limits                      └─ API-based (hosted)                ├─ Metadata columns
      └─ Rate limit schedule                                                    └─ _crawl_timestamp
                                     [2.4] ScrapeGraphAI (LLM-guided)
                                           ├─ Natural language extraction
                                           └─ Schema-mapped output
```

---

## Stage 1: URL Discovery

### Sitemap Parsing

```python
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

def discover_urls_from_sitemap(base_url: str, max_urls: int = 1000) -> list[str]:
    """Extract URLs from sitemap.xml (supports sitemap index files)."""
    sitemap_url = urljoin(base_url, "/sitemap.xml")
    urls = []

    try:
        resp = requests.get(sitemap_url, timeout=15,
                          headers={"User-Agent": "FlukeCrawler/1.0 (+https://fluke.com)"})
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Check if it's a sitemap index
        sitemaps = root.findall(".//sm:sitemap/sm:loc", ns)
        if sitemaps:
            for sm in sitemaps[:10]:  # Limit sub-sitemaps
                sub_urls = discover_urls_from_sitemap(sm.text, max_urls - len(urls))
                urls.extend(sub_urls)
                if len(urls) >= max_urls:
                    break
        else:
            for url_elem in root.findall(".//sm:url/sm:loc", ns):
                urls.append(url_elem.text)
                if len(urls) >= max_urls:
                    break

    except Exception as e:
        print(f"Sitemap discovery failed: {e}")

    return urls[:max_urls]
```

### URL Filtering

```python
import re
from urllib.robotparser import RobotFileParser

def build_url_filter(base_url: str, include_patterns: list[str] = None,
                     exclude_patterns: list[str] = None) -> callable:
    """Build a URL filter that respects robots.txt and pattern rules."""
    domain = urlparse(base_url).netloc

    # Parse robots.txt
    rp = RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    try:
        rp.read()
    except Exception:
        pass  # If robots.txt is missing, allow all

    # Default excludes (binary files, auth pages, etc.)
    default_excludes = [
        r"\.(pdf|zip|tar|gz|exe|dmg|iso|mp4|mp3|avi|mov)$",
        r"/login|/signup|/auth|/admin|/wp-admin",
        r"\?.*page=\d+$",  # Pagination (handle separately)
        r"#",  # Fragment identifiers
    ]

    compiled_includes = [re.compile(p) for p in (include_patterns or [])]
    compiled_excludes = [re.compile(p) for p in (exclude_patterns or []) + default_excludes]

    def url_filter(url: str) -> bool:
        parsed = urlparse(url)
        # Domain scope
        if parsed.netloc != domain:
            return False
        # robots.txt
        if not rp.can_fetch("FlukeCrawler", url):
            return False
        # Exclude patterns
        for pat in compiled_excludes:
            if pat.search(url):
                return False
        # Include patterns (if specified, URL must match at least one)
        if compiled_includes:
            return any(pat.search(url) for pat in compiled_includes)
        return True

    return url_filter
```

---

## Stage 2: Crawl & Extract

### Option A: Crawl4AI (Primary — JS-capable, async)

Best for: documentation sites, SPAs, JS-rendered content, large crawls.

```bash
pip install crawl4ai
crawl4ai-setup  # Install browser (one-time)
```

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def crawl_urls(urls: list[str], rate_limit: float = 1.0) -> list[dict]:
    """Crawl URLs with Crawl4AI, return clean markdown."""
    results = []
    config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,       # Cache pages locally
        word_count_threshold=50,             # Skip pages with <50 words
        excluded_tags=["nav", "footer", "header", "aside"],  # Strip boilerplate
        remove_overlay_elements=True,        # Remove popups/modals
    )

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            try:
                result = await crawler.arun(url=url, config=config)
                if result.success:
                    results.append({
                        "url": url,
                        "title": result.metadata.get("title", ""),
                        "markdown": result.markdown_v2.raw_markdown,
                        "links": result.links.get("internal", []),
                        "status_code": result.status_code,
                        "crawl_time": result.metadata.get("fetch_time", 0),
                    })
                else:
                    results.append({"url": url, "error": result.error_message})

                await asyncio.sleep(rate_limit)  # Polite delay

            except Exception as e:
                results.append({"url": url, "error": str(e)})

    return results

# Usage
urls = discover_urls_from_sitemap("https://docs.fluke.com")
results = asyncio.run(crawl_urls(urls))
```

### Option B: Trafilatura (Articles/blogs — fast, no browser needed)

Best for: news articles, blog posts, simple HTML pages.

```bash
pip install trafilatura
```

```python
import trafilatura

def extract_article(url: str) -> dict:
    """Extract clean article text with metadata."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return {"url": url, "error": "fetch_failed"}

    result = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
        output_format="json",
        with_metadata=True,
        favor_precision=True,  # Prefer precision over recall
    )

    if result:
        import json
        data = json.loads(result)
        return {
            "url": url,
            "title": data.get("title", ""),
            "author": data.get("author", ""),
            "date": data.get("date", ""),
            "markdown": data.get("text", ""),
            "categories": data.get("categories", ""),
            "tags": data.get("tags", ""),
        }
    return {"url": url, "error": "extraction_failed"}
```

### Option C: Firecrawl (Structured extraction — API-based)

Best for: when you need consistent structured output without managing browsers.

```bash
pip install firecrawl-py
```

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Single page scrape → clean markdown
result = app.scrape_url("https://docs.fluke.com/getting-started", params={
    "formats": ["markdown"],
})
print(result["markdown"])

# Crawl entire site
crawl_result = app.crawl_url("https://docs.fluke.com", params={
    "limit": 500,
    "scrapeOptions": {"formats": ["markdown"]},
})
for page in crawl_result["data"]:
    print(f"{page['metadata']['title']}: {len(page['markdown'])} chars")
```

### Option D: ScrapeGraphAI (LLM-guided extraction)

Best for: extracting specific structured data described in natural language.

```bash
pip install scrapegraphai
```

```python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "model": "azure/gpt-4.1",
    },
}

# Describe what you want in natural language
scraper = SmartScraperGraph(
    prompt="Extract all product specifications: model number, accuracy, range, certifications, price",
    source="https://www.fluke.com/en-us/product/electrical-testing/digital-multimeters/fluke-87v",
    config=graph_config,
)

result = scraper.run()
# Returns: {"model": "87V", "accuracy": "±0.05%", "range": "1000V DC", ...}
```

### Tool Selection Guide

| Tool | JS Support | Speed | Cost | Best For |
|------|-----------|-------|------|----------|
| **Crawl4AI** | Yes (headless browser) | Medium | Free | Docs sites, SPAs, large crawls |
| **Trafilatura** | No (HTML only) | Fast | Free | Articles, blogs, news |
| **Firecrawl** | Yes (API) | Medium | Paid API | Consistent output, no infra |
| **ScrapeGraphAI** | Yes (via LLM) | Slow | LLM cost | Structured extraction from complex pages |

**Default recommendation:** Start with Crawl4AI. Fall back to Trafilatura for simple pages. Use ScrapeGraphAI only for targeted structured extraction.

---

## Stage 3: Structure for RAG

### Bronze Notebook Template

```python
# Databricks notebook: Bronze_{app}_WebIngest
# Purpose: Crawl web sources and store raw markdown in Bronze Delta table.

dbutils.widgets.text("StreamName", "")
dbutils.widgets.text("Database", "flukebi_Bronze")

StreamName = dbutils.widgets.get("StreamName")
Database = dbutils.widgets.get("Database")

# Configuration from state contract
web_sources = [
    {
        "name": "fluke_docs",
        "base_url": "https://docs.fluke.com",
        "method": "crawl4ai",           # crawl4ai | trafilatura | firecrawl
        "max_pages": 500,
        "include_patterns": ["/en-us/"],
        "exclude_patterns": ["/admin/", "/api/"],
        "rate_limit_sec": 1.0,
        "depth_limit": 3,
    },
]

# Crawl and collect results
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
import asyncio, hashlib
from datetime import datetime

all_results = []
for source in web_sources:
    urls = discover_urls_from_sitemap(source["base_url"], source["max_pages"])
    url_filter = build_url_filter(source["base_url"],
                                   source.get("include_patterns"),
                                   source.get("exclude_patterns"))
    filtered_urls = [u for u in urls if url_filter(u)]
    print(f"Source '{source['name']}': {len(urls)} discovered → {len(filtered_urls)} after filter")

    results = asyncio.run(crawl_urls(filtered_urls, source.get("rate_limit_sec", 1.0)))

    for r in results:
        if "error" not in r:
            r["source_name"] = source["name"]
            r["content_hash"] = hashlib.md5(r["markdown"].encode()).hexdigest()
            r["_crawl_timestamp"] = datetime.utcnow().isoformat()
            all_results.append(r)

# Write to Bronze Delta table
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

schema = StructType([
    StructField("url", StringType()),
    StructField("title", StringType()),
    StructField("markdown", StringType()),
    StructField("source_name", StringType()),
    StructField("content_hash", StringType()),
    StructField("_crawl_timestamp", StringType()),
])

df = spark.createDataFrame(all_results, schema=schema)

# MERGE: only update if content_hash changed (incremental)
from delta.tables import DeltaTable

target_table = f"{Database}.web_raw_{StreamName}"
if DeltaTable.isDeltaTable(spark, f"/mnt/{Database}/web_raw_{StreamName}"):
    dt = DeltaTable.forName(spark, target_table)
    dt.alias("t").merge(
        df.alias("s"),
        "t.url = s.url"
    ).whenMatchedUpdate(
        condition="t.content_hash != s.content_hash",
        set={"markdown": "s.markdown", "content_hash": "s.content_hash",
             "_crawl_timestamp": "s._crawl_timestamp", "title": "s.title"}
    ).whenNotMatchedInsertAll().execute()
else:
    df.write.format("delta").mode("overwrite").saveAsTable(target_table)

print(f"Bronze: {df.count()} web pages → {target_table}")
```

### Silver Transform

```python
# Silver transforms for web content:
# 1. Deduplicate by content_hash (same content at different URLs)
# 2. Clean markdown: strip excessive whitespace, normalize headers
# 3. Extract metadata: detect language, estimate reading time
# 4. Chunk for RAG: semantic or recursive character chunking
# 5. Filter: remove thin pages (<100 words) and error pages

from pyspark.sql.functions import col, length, regexp_replace, trim

df_silver = (
    spark.table(f"flukebi_Bronze.web_raw_{StreamName}")
    .dropDuplicates(["content_hash"])
    .withColumn("markdown_clean",
        regexp_replace(col("markdown"), r"\n{3,}", "\n\n"))  # Normalize newlines
    .withColumn("word_count",
        length(regexp_replace(col("markdown_clean"), r"\S+", "x")))
    .filter(col("word_count") > 100)  # Remove thin pages
)

df_silver.write.format("delta").mode("overwrite") \
    .saveAsTable(f"flukebi_Silver.web_cleaned_{StreamName}")
```

---

## AI UCB Integration

### State Contract Flags

```json
{
  "requirements": {
    "pipeline": {
      "web_sources": [
        {
          "name": "fluke_docs",
          "base_url": "https://docs.fluke.com",
          "method": "crawl4ai",
          "max_pages": 500,
          "include_patterns": ["/en-us/"],
          "rate_limit_sec": 1.0
        }
      ]
    }
  }
}
```

### Phase Integration

```
Phase 0 (Discover):
    → Ask: "Do you have web-based data sources (documentation sites, knowledge bases, product pages)?"
    → If yes: collect base URLs, crawl config → set requirements.pipeline.web_sources[]

Phase 1 (Infra):
    → No additional resources needed (uses existing ADLS + Databricks)
    → If using Firecrawl: store API key in Key Vault

Phase 2 (Pipeline) — PRIMARY INTEGRATION:
    → Add Bronze_WebIngest notebook to ADF pipeline
    → Add Silver web_cleaned transform
    → Feed into existing Gold chunking + AI Layer embedding flow
    → ADF trigger: schedule (daily/weekly) or manual

Phase 3 (AI):
    → Web content chunks join existing AI Search index
    → content_type = "web" (filterable) for source attribution

Phase 4 (Frontend):
    → Display source URLs in citations (clickable links)

Phase 5 (Test):
    → Crawl quality checks: broken URLs, thin pages, error rate
```

---

## Resilience Patterns

### Retry with Exponential Backoff

```python
import tenacity

@tenacity.retry(
    wait=tenacity.wait_exponential_jitter(initial=2, max=60, jitter=10),
    stop=tenacity.stop_after_attempt(3),
    retry=tenacity.retry_if_exception_type((ConnectionError, TimeoutError)),
    before_sleep=lambda rs: print(f"Retry {rs.attempt_number} for URL after: {rs.outcome.exception()}"),
)
async def crawl_with_retry(crawler, url, config):
    """Crawl a single URL with retry on transient failures."""
    result = await crawler.arun(url=url, config=config)
    if not result.success and result.status_code in (429, 500, 502, 503):
        raise ConnectionError(f"HTTP {result.status_code}: {result.error_message}")
    return result
```

### Circuit Breaker (Per Domain)

```python
from collections import defaultdict
from datetime import datetime, timedelta

class DomainCircuitBreaker:
    """Stop crawling domains that consistently fail."""

    def __init__(self, failure_threshold=5, cooldown_minutes=30):
        self.failures = defaultdict(int)
        self.cooldowns = {}
        self.failure_threshold = failure_threshold
        self.cooldown_duration = timedelta(minutes=cooldown_minutes)

    def record_failure(self, domain: str):
        self.failures[domain] += 1
        if self.failures[domain] >= self.failure_threshold:
            self.cooldowns[domain] = datetime.now() + self.cooldown_duration
            print(f"Circuit OPEN for {domain} — {self.failure_threshold} consecutive failures. Cooldown: {cooldown_minutes}m")

    def record_success(self, domain: str):
        self.failures[domain] = 0
        self.cooldowns.pop(domain, None)

    def is_open(self, domain: str) -> bool:
        if domain in self.cooldowns:
            if datetime.now() < self.cooldowns[domain]:
                return True  # Still in cooldown
            else:
                del self.cooldowns[domain]  # Cooldown expired, half-open
                self.failures[domain] = 0
        return False

circuit = DomainCircuitBreaker(failure_threshold=5, cooldown_minutes=30)
```

### Crawl State Persistence (Resume After Crash)

```python
import json
from pathlib import Path

class CrawlState:
    """Persist crawl progress to disk. Resume from last checkpoint after crash."""

    def __init__(self, state_path: str = "crawl_state.json"):
        self.path = Path(state_path)
        self.state = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"completed_urls": [], "failed_urls": [], "pending_urls": [], "stats": {}}

    def save(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=2))
        tmp.replace(self.path)  # Atomic rename

    def mark_completed(self, url: str):
        if url not in self.state["completed_urls"]:
            self.state["completed_urls"].append(url)
        self.save()

    def mark_failed(self, url: str, error: str):
        self.state["failed_urls"].append({"url": url, "error": error})
        self.save()

    def get_pending(self, all_urls: list[str]) -> list[str]:
        done = set(self.state["completed_urls"])
        failed = set(f["url"] for f in self.state["failed_urls"])
        return [u for u in all_urls if u not in done and u not in failed]

    @property
    def progress(self) -> str:
        total = len(self.state["completed_urls"]) + len(self.state["failed_urls"]) + len(self.state.get("pending_urls", []))
        done = len(self.state["completed_urls"])
        failed = len(self.state["failed_urls"])
        return f"{done} completed, {failed} failed, {total - done - failed} remaining"
```

### Post-Crawl Data Quality Validation

```python
def validate_crawl_results(results: list[dict]) -> dict:
    """Validate crawl output quality before writing to Bronze."""
    total = len(results)
    errors = [r for r in results if "error" in r]
    thin = [r for r in results if "markdown" in r and len(r.get("markdown", "").split()) < 50]
    empty = [r for r in results if "markdown" in r and not r["markdown"].strip()]
    duplicates = total - len(set(r.get("content_hash", r.get("url", "")) for r in results if "error" not in r))

    report = {
        "total_urls": total,
        "successful": total - len(errors),
        "errors": len(errors),
        "error_rate": len(errors) / max(total, 1),
        "thin_pages": len(thin),
        "empty_pages": len(empty),
        "duplicates": duplicates,
    }

    # Quality gate
    if report["error_rate"] > 0.30:
        print(f"WARNING: High error rate ({report['error_rate']:.0%}). Check source availability.")
    if report["thin_pages"] > total * 0.50:
        print(f"WARNING: >50% thin pages. Check content extraction quality.")

    return report
```

---

## Rate Limiting & Politeness

| Setting | Default | Production | Notes |
|---------|---------|------------|-------|
| Requests/sec | 1.0 | 0.5-2.0 | Respect target server capacity |
| Concurrent connections | 1 | 3-5 | Max for polite crawling |
| Retry on 429 | 3x with exponential backoff | Same | Always honor Retry-After header |
| Retry on 5xx | 2x with 30s delay | Same | Server may be temporarily overloaded |
| robots.txt | Always respect | Always respect | Non-negotiable |
| User-Agent | `FlukeCrawler/1.0` | Same | Identify yourself |
| Cache TTL | 24h | 7d | Re-crawl frequency |

---

## Anti-Patterns (NEVER Do These)

1. **NEVER ignore robots.txt.** Non-negotiable. Getting blocked helps nobody and can create legal liability.
2. **NEVER crawl without rate limiting.** Default 1 req/sec. Exceeding this can trigger IP bans and DDoS protection that blocks future crawls permanently.
3. **NEVER retry infinitely on 429/5xx.** Use `tenacity` with `stop_after_attempt(3)` and exponential backoff. Infinite retries compound server pressure.
4. **NEVER skip content hash deduplication.** The same content can appear at multiple URLs (canonical vs alias). Without content_hash dedup, Bronze contains duplicates that inflate index size and degrade retrieval quality.
5. **NEVER crawl without state persistence.** Large crawls (500+ pages) WILL be interrupted. Without `CrawlState`, you restart from zero every time — wasting compute and hammering the target server.
6. **NEVER write to Bronze without post-crawl validation.** Check error rate, thin pages, and duplicates BEFORE writing. Loading garbage into Bronze propagates through Silver → Gold → AI Search.
7. **NEVER use ScrapeGraphAI for bulk crawling.** It makes an LLM call per page — use it only for targeted extraction of specific structured data from a handful of pages.
8. **NEVER hardcode domain-specific selectors.** Use Crawl4AI's `excluded_tags` for general boilerplate removal. If you need domain-specific selectors, put them in the state contract, not in the crawler code.

## Error Recovery

| Error | Recovery |
|-------|---------|
| 429 Too Many Requests | Honor `Retry-After` header, reduce rate_limit_sec, increase delay between batches |
| Timeout on JS-heavy pages | Increase Crawl4AI timeout, try Trafilatura as fallback (no JS), consider Firecrawl API |
| Empty markdown for valid pages | Page uses heavy JS — ensure Crawl4AI headless browser is installed (`crawl4ai-setup`), try scroll + wait |
| Circuit breaker opens for domain | Check if site is down, wait for cooldown, reduce concurrency when circuit half-opens |
| Crawl state corrupted | Delete `crawl_state.json`, restart crawl from scratch (Bronze MERGE handles dedup) |
| Content hash collision (unlikely) | Switch from MD5 to SHA-256 for content hashing |
| Sitemap returns 404 | Fall back to recursive link discovery from seed URL |

---

## Dependencies

```
crawl4ai>=0.3           # Primary crawler (JS-capable)
trafilatura>=1.6        # Article extraction (fast, no browser)
# Optional:
firecrawl-py>=0.1       # Structured extraction (API-based, paid)
scrapegraphai>=1.0      # LLM-guided extraction
```

---

## References

- [Crawl4AI Documentation](https://docs.crawl4ai.com/)
- [Trafilatura Documentation](https://trafilatura.readthedocs.io/)
- [Firecrawl Documentation](https://docs.firecrawl.dev/)
- [ScrapeGraphAI Documentation](https://scrapegraph-ai.readthedocs.io/)
