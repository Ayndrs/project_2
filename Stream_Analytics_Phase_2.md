# Project Spec: StreamFlow Phase 2 — Enterprise Analytics (Databricks)

## 1. Executive Summary

**StreamFlow** is an analytics path that ingests **Kafka**-backed e-commerce activity, processes it with **PySpark** and **Apache Airflow**, loads results into **Databricks** using **Delta Lake** and a **medallion-style** layout, and surfaces metrics through **Streamlit**—the **same app** the Project 2 **internal business agent** cohort uses for chat and scoring. **Power BI** against Databricks is an optional stretch if your cohort wants BI tooling.

**Program context:** [PROJECT_2_MASTER.md](PROJECT_2_MASTER.md) | **ML feature reference (for agent integration):** [data/README.md](data/README.md)

---

## 2. Functional modules (what DE typically owns)

### A — Databricks medallion + orchestration

**Goal:** Reliable **Delta** tables from Phase 1 outputs and clear refresh behavior.

**Typical ingredients:**

- **Airflow DAG** (name up to you) that either syncs files to storage consumed by loaders **or** triggers Databricks Jobs that read landing paths. Include retries and basic error handling where you can.  
- **Bronze / Silver / Gold** tables—exact names are yours; many cohorts use a pattern like the table below.

| Layer | Role | Example objects (illustrative) |
|-------|------|--------------------------------|
| **Bronze** | Raw or minimally typed landings | `raw_user_events`, `raw_transactions`, `raw_products`, `raw_customers` |
| **Silver** | Cleaned, typed, flattened | `stg_user_events`, `stg_transactions`, `stg_transaction_items`, `stg_products`, `stg_customers` |
| **Gold** | Star-schema style analytics | `dim_customer`, `dim_product`, `dim_date`, `fact_transactions`, `fact_user_activity`, `agg_daily_revenue` |

**Agent handoff:** Coordinate with the AI track early so Gold (or a **view** such as `gold.v_order_features`) can supply **order-level features** aligned with [data/README.md](data/README.md) when you are ready—shape and schedule are a **team decision**, not fixed here.

> [!WARNING]
> **Kafka batch consumer:** In most Phase 2 setups the consumer runs as a **standalone script** (like producers), **not** as an Airflow task. Remove or avoid consumer tasks inside the DAG if your Phase 1 spec says so.

---

### B — Dimension data (starter kit)

Producers often read from static JSON so IDs in events line up with dimensions:

| File | Rough size | Role |
|------|------------|------|
| `data/products.json` | ~2k products | Catalog for `dim_product` |
| `data/customers.json` | ~1k customers | Profiles for `dim_customer` |

**Product fields** (typical): `product_id`, `product_name`, `description`, `category`, `subcategory`, `brand`, `manufacturer`, `msrp`, `cost_price`, `created_date`, `is_active`

**Customer fields** (typical): `user_id`, `email`, `first_name`, `last_name`, `registration_date`, `account_type`, `date_of_birth`, `loyalty_points`, `state`

Your trainer’s repo may place these under `assets/` or similar—follow your cohort’s layout.

---

### C — Streamlit (metrics) + shared app

**Goal:** **Same Streamlit entrypoint** as the internal business agent: **Metrics** page driven by **Databricks SQL** against Gold; **Chat** owned by the AI track. **Pair-program** navigation, env-based secrets, and layout ([PROJECT_2_MASTER.md](PROJECT_2_MASTER.md)).

**Ideas for metrics:** revenue, active users, conversion-style funnel, category mix—whatever tells a clear story from your facts and aggregates. Start simple; add polish if time allows.

**Stretch — Power BI:** Connect to Databricks (Import or DirectQuery) and build a small model if your cohort assigns it.

---

## 3. Example catalog layout (yours may differ)

```
<CATALOG>.<your_team>_streamflow   (example name)
├── bronze
│   ├── raw_user_events
│   ├── raw_transactions
│   ├── raw_products
│   └── raw_customers
├── silver
│   ├── stg_user_events
│   ├── stg_transactions
│   ├── stg_transaction_items
│   ├── stg_products
│   └── stg_customers
└── gold
    ├── dim_customer
    ├── dim_product
    ├── dim_date
    ├── fact_transactions
    ├── fact_user_activity
    ├── agg_daily_revenue
    └── (optional view for ML lookups, e.g. v_order_features)
```

Document the names you actually ship in your README.

---

## 4. What you’re expected to deliver

| Deliverable | Notes |
|-------------|--------|
| Kafka batch consumer (if Phase 1 scope includes it) | Feeds landing / pipeline per your Phase 1 design |
| Databricks notebooks or jobs | Ingestion + transforms; **Delta** Bronze/Silver/Gold |
| Scheduled pipeline | Jobs / Workflows / DLT—your choice |
| Airflow DAG | Triggers sync or Databricks runs |
| Streamlit metrics | KPIs from Gold via Databricks SQL; shared app with agent cohort |
| Presentation (~20 min, joint) | Pipeline walkthrough + **architecture diagram** (see [PROJECT_2_MASTER.md](PROJECT_2_MASTER.md) §8) |
| Optional | Power BI; heavier load tests; extra Gold features for ML experiments |

---

## 5. Technical constraints & habits

| Topic | Guidance |
|-------|------------|
| **Databricks** | Right-size SQL warehouse and job clusters; **stop** idle warehouses; partition large tables by date where it helps |
| **Streamlit** | Local or cohort host; credentials via **environment variables**, never committed |
| **Volume** | Often **50k+** events in bulk mode; scale in steps and watch cost |
| **Phase 1** | Phase 2 assumes Phase 1 landing / CSV output exists |
| **Docker** | Many cohorts keep Phase 1 `docker-compose` unchanged; Databricks + Streamlit often run **outside** Docker—follow your trainer |

---

## 6. Scale, cost, and optional depth

- **Push volume gradually**; note latency and spend.  
- **Optional challenge:** Extra **Gold** features (rolling metrics, session-based fields) for experimental models—pair with ML; don’t block your baseline on perfection.

---

## 7. Related documentation

- [PROJECT_2_MASTER.md](PROJECT_2_MASTER.md) — cohort vision, planning, presentation  
- [PROJECT_2_AGENT.md](PROJECT_2_AGENT.md) — internal business agent, Streamlit chat  
- [data/README.md](data/README.md) — feature columns for model / lookup alignment  
- [Phase 1 Specification](https://github.com/120925-Data-Engineering/trainer-code/blob/main/Project-Specs/Project-1/Stream_Analytics_Platform.md)  
- [Group Assignments](https://github.com/120925-Data-Engineering/trainer-code/blob/main/Project-Specs/Project-2/Groups.md)
