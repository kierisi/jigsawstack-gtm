# JigsawStack GTM Engine 🚀

An autonomous Go-To-Market pipeline built with the JigsawStack SDK — architected to extract high-intent signals from developer forums and transform unstructured noise into enriched, actionable lead state.

---

## 🏗️ The "Interfaze" Architecture

This engine is inspired by the Context-Centric Architecture defined in [Interfaze (arXiv:2602.04101v1)](https://arxiv.org/abs/2602.04101v1). It offloads expensive LLM reasoning by utilizing JigsawStack's specialized **Small Language Models (SLMs)** for perception and classification.

---

## The Three-Stage Engine

### 1. 🌾 The Intent Harvester · `intent-harvester.py`
|||
|---|---|
| **Layer** | Context Construction |
| **Goal** | Macro-level prospecting across Hacker News |

Scans multiple pages for AI/ML keywords, handles pagination, and extracts metadata.

> **Technical Detail — Column-Zipping:** Implements custom logic to reassemble JigsawStack's grouped DOM responses into row-based lead records.

---

### 2. 🎯 The Autonomous Scorer · [`comment-scorer.py`](https://github.com/kierisi/jigsawstack-gtm/blob/main/comment-scorer.py)

|---|---|
| **Layer** | Action Layer / Controller |
| **Goal** | Deep-dive intent analysis via Algolia-backed search |

Autonomously identifies top relevant threads (e.g., `"PDF OCR"`) and uses the `ai_scrape` model to extract specific developer pain points.

---

### 3. 🔗 The Sentiment Chain · `comment-scorer-sentiment.py`

|---|---|
| **Layer** | Specialized Model Chain |
| **Architecture** | `ai_scrape` (DOM Extraction) → `sentiment` API (Evaluation) |

> **The "SLM Moat":** By chaining a purpose-built sentiment model rather than a general LLM, we eliminate scoring hallucinations and significantly reduce token latency.

---

### 🚀 Real-World Implementation & Orchestration

Beyond the core Python engine, this system is designed to plug into a production-grade GTM stack.

**Sumble Intent Trigger:** The pipeline begins with Sumble. By leveraging Sumble's knowledge graph (instead of blindly scraping Hacker News), we identify companies showing active "buyer intent" (e.g., technical migrations or hiring for specialized AI roles). This acts as the macro-trigger for the JigsawStack engine to begin targeted context extraction.

**The n8n Orchestrator:** The Python scripts act as custom worker nodes within an n8n workflow. Every "High Intent" signal detected by the Sentiment Chain triggers a webhook that starts the downstream enrichment process.

**Clay Enrichment:** Leads are pushed to a Clay table via API. Here, the "Distilled Context" from JigsawStack is augmented with technographic data (e.g., "Is this user's company using AWS or GCP?") and social proof (LinkedIn/GitHub activity).

**Automated Warm-Outbound:** Finalized, enriched leads are synced to a CRM (Attio/HubSpot) or a sending tool (Instantly/Lemlist). The outreach is triggered automatically, referencing the exact pain point extracted from the original forum post.

## ⚡ AI-Native Development Workflow

This project was built using a **"Vibe Coding" / AI-First** workflow. From architectural concept to functional SDK implementation: **under 2 hours.**

**Velocity:** Rapid iteration on the Column-Zipping logic was handled via real-time LLM debugging — enabling 10x faster shipping than traditional manual syntax entry.

**The Philosophy:** Code is a disposable artifact of the logic. The value is in System Architecture and Data Strategy where the LLM handles the boilerplate.

---

## ⚔️ Technical War Stories

*Lessons learned while stress-testing the JigsawStack beta in a production-style environment.*

### 🛡️ The Column-Zip Quirk
Early iterations assumed standard row-based JSON returns. The Harvester was refactored to handle JigsawStack's high-efficiency grouping of DOM attributes by prompt-key — enabling significantly faster processing of multi-element scrapes.

### 📉 Deterministic Evaluation & Scaling
Initial prompts allowed for "scoring bloat" (hallucinated values). Moving to a **Deterministic API Chain (Small Models)** corrected edge cases where general LLMs hallucinated 10-digit scores for simple frustration signals.

### 🚧 Scalability & Rate-Limit Management
High-velocity stress tests triggered `429 Too Many Requests`.

**The Solution:** Implemented an 800-character truncation step for long-form "HN Essays" to stay within schema validation limits.

**The Roadmap:** Future iterations will use an Exponential Backoff controller in the Action Layer to manage concurrency across a global VPC.

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| **Core** | JigsawStack SDK (AI Scrape, Sentiment, Selectors) |
| **Orchestration** | Python |
| **Workflow** | AI-First / Vibe Coding |
| **Data Sources** | Hacker News |

---

*Built as a GTM Engineering proof-of-concept.*
