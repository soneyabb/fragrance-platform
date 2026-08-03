# Sillage — Fragrance Ingredient Intelligence Platform

> A multi-source fragrance ingredient intelligence platform integrating chemistry, regulation, sensory, and market data.

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---
![Sillage Dashboard](assets/demo.gif)
---


## Overview

Fragrance ingredient data is scattered across chemistry databases, regulatory bodies, academic papers, and consumer platforms — with no unified view.

**Sillage** integrates five public data sources into a single ingredient-level intelligence pipeline, with provenance tracked at every layer. At its core: **66 ingredients personally curated through direct olfactory experience** — the layer no public database provides.

---

## Motivation

This project was built to demonstrate two things simultaneously:

1. **Fragrance domain expertise** — personal sensory curation, IFRA regulatory knowledge, industry application mapping
2. **Data engineering capability** — multi-source ETL pipeline, SQLite data modeling, Streamlit dashboard architecture

Target audience: R&D roles at global beauty and fragrance companies (L'Oréal, Givaudan, Firmenich), and graduate program applications (ISIPCA).

---

## Features

| Page | Description |
|---|---|
| **① Ingredients** | Per-ingredient view: chemical data, sensory notes, IFRA regulation, market occurrence, industry signals |
| **② Compare** | Side-by-side comparison of up to 5 ingredients with cosine similarity matching |
| **③ Connections** | Interactive network graph: Ingredient × Industry × Odor Family |
| **④ Market** | Occurrence analytics across 59,325 perfumes (Parfumo 2024 snapshot) |
| **⑤ Intelligence** | Real-time signals: Reddit r/fragrance, industry news, academic papers |
| **⑥ Blend** | Blend simulator + sensory language → ingredient mapping |

---

## Architecture

```
Data Sources
     │
     ├── PubChem API          (CAS, molecular formula, molecular weight)
     ├── IFRA 51st Amendment  (regulatory limits, 18 application categories)
     ├── Pyrfume              (odor descriptors — GoodScents + Leffingwell)
     ├── Parfumo TidyTuesday  (59,325 perfume profiles, 2024 snapshot)
     └── Semantic Scholar     (academic research signal)
     │
Collectors (Python)
     │
   SQLite
(329 ingredients · 4 data layers)
     │
Streamlit Dashboard
(6 pages · Plotly · PyVis · scikit-learn)
```

### Data Quality Tiers

| Tier | Description | Count |
|---|---|---|
| ★★★ CURATED | Personally evaluated — full 4-layer data | 66 ingredients |
| ★★☆ MAPPED | Auto-mapped — chemical + odor descriptors | ~200 ingredients |
| ★☆☆ REGISTERED | IFRA-registered — material layer only | ~63 ingredients |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Dashboard | Streamlit |
| Database | SQLite |
| Data Pipeline | Python 3.12 (requests, pandas) |
| Visualization | Plotly, NetworkX, PyVis |
| Similarity | scikit-learn (cosine similarity) |
| Data Sources | PubChem API, IFRA, Pyrfume, Parfumo, Semantic Scholar |
| Deployment | Streamlit Cloud |

---

## Getting Started

```bash
# 1. Clone
git clone https://github.com/soneyabb/fragrance-platform.git
cd fragrance-platform

# 2. Install dependencies
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env — Reddit API credentials optional; dashboard works without it

# 4. Run the data pipeline
python collectors/pubchem_collector.py
python collectors/ifra_collector.py
python collectors/pyrfume_collector.py
python collectors/scholar_collector.py
python processors/load_to_db.py

# 5. Launch
streamlit run dashboard/app.py
```

---

## Current Progress

- ✅ 5-source data pipeline (329 ingredients)
- ✅ SQLite with regulatory, chemical, sensory, and academic layers
- ✅ 6-page Streamlit dashboard
- ✅ Cosine similarity–based ingredient matching
- ✅ Parfumo market analytics (59,325 perfumes)
- 🔄 Reddit community signal (API key setup in progress)
- 🔄 Streamlit Cloud deployment in progress

---

## Future Work

- AWS migration: SQLite → RDS, collectors → Lambda + EventBridge
- AI-generated highlight quotes from personal sensory notes (Claude API)
- Odor threshold visualization and GC-MS data integration
- Reddit trend analysis (r/fragrance)

---

## Data Sources & Licensing

| Source | Terms |
|---|---|
| PubChem | Public domain (NIH) |
| IFRA 51st Amendment | Public — non-commercial |
| Pyrfume (GoodScents, Leffingwell) | Open data |
| Parfumo TidyTuesday | Non-commercial use only |
| Semantic Scholar | Open access API |
| Personal sensory data | Original — direct olfactory evaluation |
