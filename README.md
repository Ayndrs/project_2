# Stream Analytics Platform

An end-to-end e-commerce analytics platform that combines a real-time Kafka → Databricks data pipeline, a SageMaker-hosted predictive model, and a LangChain agent — all surfaced through a single internal Streamlit app.

This repo was built as a two-part capstone project (model training + deployment, then a streaming pipeline + internal agent), and the structure below reflects that progression.

## What this is

Three things stitched into one internal tool for e-commerce operations staff (support, risk/fraud, merchandising — **not** customers):

1. **A predictive model** — XGBoost on SageMaker, trained on historical orders to predict 90-day customer lifetime value (with churn and return-risk as alternative targets).
2. **A streaming data pipeline** — Kafka producers simulate user and transaction events, which flow through Spark Structured Streaming into a Databricks Delta Lake (Bronze → Silver → Gold), orchestrated by Airflow.
3. **An internal business agent** — A ReAct-style LangChain agent that looks up orders, calls the SageMaker endpoint to score them, and answers policy questions via retrieval-augmented generation over a company policy document — all from a shared Streamlit app alongside a Gold-layer metrics dashboard.

## Repository layout

```
.
├── PROJECT_1_MODEL.md              # Spec: model training + SageMaker deployment
├── PROJECT_2_MASTER.md             # Spec: Phase 2 vision (DE + agent, shared app)
├── PROJECT_2_AGENT.md              # Spec: agent/Streamlit/policy RAG details
├── Stream_Analytics_Phase_2.md     # Spec: data engineering / Databricks build
├── basic-arch.png                  # Architecture diagram
├── requirements.txt
│
├── data/
│   ├── transaction_events_producer.py   # Kafka producer: transaction_events topic
│   ├── user_events_producer.py          # Kafka producer: user_events topic
│   ├── products.json                    # ~2k product dimension records
│   └── customers.json                   # ~1k customer dimension records
│
├── kafka/
│   └── consumer.ipynb              # Spark Structured Streaming consumer (Kafka → Bronze)
│
├── ETL/
│   ├── silver.ipynb                # Bronze → Silver cleaning/typing
│   └── gold.ipynb                  # Silver → Gold star-schema (dims + facts)
│
├── airflow/
│   ├── docker-compose.yaml         # Local Airflow stack
│   ├── Dockerfile
│   └── dags/databricks_dag.py      # Triggers the Databricks job from Airflow
│
├── app/                            # Streamlit entry point (Gold dashboard + chat)
│   ├── app.py
│   └── pages/
│       ├── metrics.py              # Revenue, active users, category mix from Gold
│       └── chat.py
│
├── streamlit/                      # LangChain agent backing the Chat page
│   ├── ingest_policy.py            # Chunks/embeds the policy compendium into Pinecone
│   ├── pages/agent_chat.py
│   └── agent/
│       ├── executor.py             # Agent setup: LLM, tools, memory, system prompt
│       └── tools/
│           ├── lookup.py           # Order lookup (CSV for demo data, Databricks for live data)
│           ├── scoring.py          # Encodes a row and calls the SageMaker endpoint
│           ├── policy_rag.py       # Pinecone similarity search over policy text
│           └── product.py          # Product lookup from products.json
│
├── view_data/
│   └── v_order_features.csv        # Snapshot of the Gold feature view used for scoring
│
└── Generic E-Commerce Company_ Master Policy Compendium.docx   # RAG source document
```

## Architecture

```
Kafka producers ─▶ Spark Structured Streaming ─▶ Databricks Delta (Bronze → Silver → Gold)
   (user_events,          (kafka/consumer.ipynb)         (ETL/silver.ipynb, ETL/gold.ipynb)
    transaction_events)                                            │
                                                                    ▼
                                                      Airflow DAG triggers Databricks job
                                                                    │
                                  ┌─────────────────────────────────┴──────────────────────┐
                                  ▼                                                         ▼
                     Streamlit "Metrics" page                                  LangChain agent ("Chat" page)
                  (Databricks SQL against Gold)                 (order lookup → SageMaker scoring → policy RAG)
                                                                                    │
                                                                       SageMaker XGBoost endpoint
                                                                     (trained in Project 1, see below)
                                                                                    │
                                                                    Pinecone vector store
                                                                (policy compendium, citations)
```

The two tracks meet in one Streamlit app: a **Metrics** page reading Gold tables via Databricks SQL, and a **Chat** page backed by the LangChain agent.

## Part 1 — Predictive model

Trained on a historical dataset of e-commerce orders to predict outcomes that aren't knowable at order time:

| Target | Type | Column |
|---|---|---|
| 90-day customer lifetime value | Regression | `customer_ltv_90d` |
| 60-day churn | Binary classification | `churned_within_60d` |
| Order return | Binary classification | `returned_order` |

The implemented agent tool (`scoring.py`) scores **`customer_ltv_90d`** in production, against an exact 39-column feature vector (one-hot encoded category/payment/currency/device fields) the SageMaker endpoint was trained on. See `PROJECT_1_MODEL.md` for the full model-development spec (EDA, baseline, XGBoost training, SHAP explainability, SageMaker deployment via Model Registry).

## Part 2 — Streaming pipeline

- **Producers** (`data/`) generate synthetic `user_events` and `transaction_events`, joined against the static `products.json` / `customers.json` dimension files so IDs line up downstream. Each producer supports real-time streaming, bulk historical backfill, or both:
  ```bash
  # Stream events in real time (1 event every 2s)
  python data/transaction_events_producer.py

  # Bulk-generate 10,000 historical transactions, then keep streaming
  python data/transaction_events_producer.py --bulk --count 10000 --continue-after
  ```
- **Spark Structured Streaming** (`kafka/consumer.ipynb`) reads both topics with explicit schemas and lands them as Bronze tables.
- **ETL notebooks** (`ETL/silver.ipynb`, `ETL/gold.ipynb`) clean/type the Bronze data into Silver, then build a Gold star schema (`dim_customer`, `dim_product`, `fact_transactions`, `fact_user_activity`, etc.) plus a feature view (`v_order_features`) that mirrors the model's training columns for agent lookups.
- **Airflow** (`airflow/dags/databricks_dag.py`) triggers the Databricks job that runs the pipeline; the rest of the Airflow scaffolding (Dockerfile, docker-compose) runs it locally.

See `Stream_Analytics_Phase_2.md` for the full data-engineering spec.

## Part 3 — Internal business agent

A ReAct agent (`streamlit/agent/executor.py`, via `langchain.agents.create_react_agent` + GPT-4o) with four tools:

| Tool | What it does |
|---|---|
| `OrderLookup` | Fetches an order's feature row — from the training CSV for `ORD-`-prefixed demo IDs, or from the Databricks Gold view for live UUID order IDs |
| `ScoreOrder` | Encodes the row and invokes the SageMaker endpoint, returning predicted LTV, a risk tier, top contributing factors, and a suggested next step |
| `PolicyRAG` | Embeds the question and searches a Pinecone index built from the Master Policy Compendium, returning grounded text for the agent to cite |
| `ProductInfo` | Looks up category, warranty, and return-window info from `products.json` |

The system prompt scopes the agent to internal staff, forbids it from inventing scores or policy, and restricts it to read-only actions (no refunds or account changes). `streamlit/ingest_policy.py` handles the one-time chunk/embed step that populates the Pinecone index from the `.docx` compendium.

See `PROJECT_2_AGENT.md` for the full agent/RAG spec and `PROJECT_2_MASTER.md` for how the two project tracks (data engineering and agent) share one Streamlit app.

## Running it

This is a learning-project repo assembled from course specs rather than a one-command deployable app — pieces (Kafka, Airflow, Databricks, SageMaker, Pinecone) are meant to be stood up individually. Roughly:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set environment variables** (a `.env` file is expected at the repo root and is loaded by both the Streamlit pages and the agent tools):
   - `DATABRICKS_ACCESS_TOKEN`, `SERVER_HOSTNAME_TOKEN`, `HTTP_PATH_TOKEN` — for the Metrics page
   - `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DATABRICKS_TOKEN` — for live order lookups
   - `SAGEMAKER_ENDPOINT`, `AWS_REGION` — for scoring
   - `OPENAI_API_KEY` — for the agent LLM and embeddings
   - `PINECONE_API_KEY` — for policy retrieval
3. **Stand up Kafka locally** and run the producers in `data/` to generate events.
4. **Run the Spark consumer** (`kafka/consumer.ipynb`) against your Kafka broker to land Bronze data, then run `ETL/silver.ipynb` and `ETL/gold.ipynb` in Databricks.
5. **Deploy the SageMaker endpoint** per `PROJECT_1_MODEL.md`, and ingest the policy document with `streamlit/ingest_policy.py`.
6. **Launch the app**:
   ```bash
   streamlit run app/app.py
   ```

## Project specs

The `.md` files at the repo root are the original assignment specifications this project was built against, and are kept for reference:

- `PROJECT_1_MODEL.md` — model training and SageMaker deployment
- `PROJECT_2_MASTER.md` — overall Phase 2 vision and cadence
- `Stream_Analytics_Phase_2.md` — data engineering / Databricks build
- `PROJECT_2_AGENT.md` — agent, Streamlit, and policy RAG details
