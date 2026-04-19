# Project 2: Internal Business Agent (e-commerce)

**Skills:** Develop LangChain Applications  
**Duration:** ~2 weeks (group sprint)  
**Team:** You work with a **data engineering** cohort on one shared Streamlit experience ([PROJECT_2_MASTER.md](PROJECT_2_MASTER.md)).  
**Delivery:** ~20 min team presentation + **Streamlit** (chat + metrics) + working demo  
**Prerequisite:** SageMaker model trained on the cohort dataset ([data/README.md](data/README.md)); instructor reference ok if needed  

**Also read:** [PROJECT_2_MASTER.md](PROJECT_2_MASTER.md) (big picture) | [Stream_Analytics_Phase_2.md](Stream_Analytics_Phase_2.md) (DE side)

---

## Audience (scope)

The agent is for **internal business use only**—people who run the company’s operations: **customer support leads**, **risk / fraud analysts**, **merchandising or strategy**, **team managers**, and similar roles. They use it to **research orders**, **assess model scores**, and **interpret policy** while supporting decisions.

It is **not** for **end customers**, **shoppers**, or a **public-facing** support site. Do not design flows, tone, or guardrails as if the chat user were a buyer; frame prompts, system instructions, and demos around **employees** acting on behalf of the business.

---

## What you’re building

You already trained an **XGBoost** model on e-commerce orders. Now you wrap it in a **LangChain** agent with **tools**: scoring, order lookup, product-oriented help, and **retrieval** over the **`Generic E-Commerce Company_ Master Policy Compendium.docx`** so policy answers are **grounded** (citations—not invented text).

The **LLM** routes and explains; **scores** come from **SageMaker**; **policy** comes from your **vector store** (or similar) over the compendium. Your DE partners feed **Databricks** into the same **Streamlit** app for **metrics** when ready.

**Optional stretch:** Extra engineered features, new prediction targets, additional endpoints, richer analytics, MLOps-style retraining—if time and energy allow; keep a short note in your repo so others can follow what you built.

---

## Before you code

- **Redeploy** the endpoint (or use an instructor-approved reference artifact).  
- **Know** your model: input format (column order, encodings for categoricals), output interpretation, and **SHAP** (or similar) so the agent can explain *why* a score is high or low—not guess.  
- **Sync with DE** using [data/README.md](data/README.md) as the feature reference. Many teams start **lookup** from the CSV or a small **SQLite** DB, then switch to **Databricks** Gold or a view when DE is ready—decide together and write it down somewhere your team reads.

---

## Tools (building blocks)

These are the usual pieces; names and signatures are yours.

- **Scoring** — A LangChain tool that builds the **numeric payload** your endpoint expects (same logic as training), calls **SageMaker**, parses the response, and returns something useful (probability, tier, a short human-readable line). If you have multiple models, you can expose multiple tools or one tool with a parameter—your design.  
- **Order lookup** — Given an `order_id`, return the **feature row** the scoring tool needs. Source can evolve from file → DB → lakehouse.  
- **Product info** — Something that answers product/category questions (warranties, return windows, category quirks). Static rules, small JSON, or a thin tool—whatever fits.  
- **Policy RAG** — Separate from generic product info: the **compendium** is the authority for returns, eligibility, shipping rules, etc. See below.

---

## Agent behavior

- **Pattern:** A **ReAct**-style (or equivalent) agent that **chooses tools** based on the user, can **chain** (e.g. lookup then score), and **never invents model outputs**—if the user needs a score, the scoring tool runs.  
- **System prompt:** Set an **internal operator** role (not a storefront assistant), what the model predicts, limitations, SHAP-style context, and **boundaries** (e.g. the agent does not execute refunds or account changes—only informs).  
- **Memory:** Enough **conversation memory** for follow-ups (“look up that order,” “now score it,” “compare to ORD-…”).  
- **Structured output:** For scoring-style answers, a **consistent shape** helps (e.g. order id, `user_id` from the data row, prediction, tier, factors, suggested **internal** next step—use Pydantic, JSON, or whatever your stack supports).  
- **Guardrails:** Refuse off-topic asks, out-of-authority actions (e.g. “process this refund,” “cancel this for the shopper” as if the tool were the system of record), and handle missing orders or endpoint errors without crashing the UX—even when the **internal** user phrases the request like a customer might.

---

## Streamlit

- **One app** for **internal** users: **chat** (agent) and a **metrics** area (DE usually owns SQL against Gold). **Pair-program** so secrets, layout, and navigation stay coherent. This is a **business console**, not a customer portal.  
- **Alerts in chat (optional but common):** When a score crosses a threshold **you** define in code/config, or when policy retrieval surfaces a hard rule, many teams show a small **banner or badge**—driven from **model output** or **retrieved text**, not from the LLM making up a flag.

---

## Policy RAG (Master Policy Compendium)

- **Source:** `Generic E-Commerce Company_ Master Policy Compendium.docx` (path as provided by your cohort).  
- **Ingestion:** Extract text from the docx (loaders, `python-docx`, export to markdown—your choice), **chunk**, **embed**, and build an index. Cache embeddings in dev if you pay per call.  
- **Runtime:** **Retrieve** relevant chunks, **answer** with **citations** (section, chunk id, or short quote). **Do not** contradict retrieved text; if retrieval finds nothing useful, say so and suggest human support.  
- **Guardrails** align with policy: don’t promise actions the agent can’t perform; don’t invent policy when retrieval is empty.

---

## What a solid demo usually shows

Not a script—just the kind of story that proves the system works for **internal** users:

- An **ops-style** turn: lookup → score → explanation tied to **real** features and SHAP context.  
- A **policy** question an employee would ask (eligibility, windows, rules) answered from the **compendium** with a **citation**.  
- A **follow-up** turn that uses **memory**.  
- A **guardrail** (e.g. off-topic, or a request to **execute** a shopper action the agent cannot perform).  
- Optional: a **visible alert** when scores or policy warrant it.  
- **Cleanup:** Tear down SageMaker resources after demo per your instructor’s cloud rules.

---

## Presentation (~20 min)

Joint **~20 min** presentation with DE: requirements (architecture diagram, demo, collaboration) are in [PROJECT_2_MASTER.md](PROJECT_2_MASTER.md) §8.

---

## Cross-team

**DE** needs your **feature and encoding story** to shape Gold. **You** need **scores**, **policy**, and **UX** in one **Streamlit**. Check in early, demo however tells your story best.
