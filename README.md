# 💊 Pharmacy Demand Signal – Rule-Based Agentic AI System

This project implements a **rule-based, multi-agent demand intelligence system** for pharmacies.  
It analyzes **daily sales data**, detects **demand trends**, generates **stocking recommendations**, and produces a **human-readable Demand Signal Report**.

✅ No Machine Learning  
✅ No LLMs  
✅ Fully Explainable  
✅ Deterministic & Auditable  
✅ Production-Style Agent Architecture  

---

## 🌐 Live Demo

You can try the live deployed app here:

👉 https://pharma-demand-signal-agentic.onrender.com

Upload a store-wise pharmacy sales CSV to generate a real-time Demand Signal Report.


## 🚀 What This System Does

Given a CSV with **store-wise daily pharmacy sales**, the system:

1. ✅ Loads & validates raw sales data  
2. ✅ Aggregates store-level demand into product-level demand  
3. ✅ Detects demand trends using **pure rule-based logic**
4. ✅ Converts trends into **stocking recommendations**
5. ✅ Generates a **Daily Demand Summary Report**
6. ✅ Provides a **Streamlit UI** for CSV upload & report download

---

## 🧠 Core Capabilities

| Capability | Description |
|-----------|------------|
| Trend Detection | Increasing, Decreasing, Stable, Spiky |
| Algorithms Used | Moving Averages, % Change, Volatility Index |
| Decision Logic | Threshold-based expert rules |
| Explainability | Full human-readable reasoning |
| UI | Streamlit frontend |
| Input Data | Store-wise daily sales CSV |
| Output | Demand Signal Report (TXT) |

---

## 🧩 Multi-Agent Architecture

This is a **true Agentic System** built using **task-specialized deterministic agents**:

CSV Upload
↓
Data Loader Agent
↓
Store Aggregation Agent
↓
Trend Detector Agent
↓
Demand Insight Agent
↓
Report Generator Agent
↓
Daily Demand Signal Report


### ✅ Agents Explained

| Agent | Responsibility |
|------|----------------|
| **DataLoaderAgent** | Loads & validates input CSV |
| **StoreAggregationAgent** | Aggregates multi-store demand |
| **TrendDetectorAgent** | Detects demand using custom rules |
| **DemandInsightAgent** | Converts trends → stock actions |
| **ReportGeneratorAgent** | Generates executive-ready report |

This follows:
- ✅ **Pipeline Pattern**
- ✅ **Expert System Design**
- ✅ **Single Responsibility Principle**
- ✅ **Deterministic AI Architecture**

---


---

## 📊 Trend Detection Logic (No ML)

For each product (after store aggregation):

1. Use the **last 7 days** of sales (configurable)
2. Compute:
   - Recent average
   - Last day sales
   - Percentage change vs average
   - Volatility index (std / mean)
3. Classification Rules:
   - **Increasing** → strong upward % change + positive daily momentum
   - **Decreasing** → strong downward % change + negative momentum
   - **Stable** → within ±20% of recent average
   - **Spiky** → high volatility or single-day extreme jumps
   - **Insufficient Data** → less than 3 days available

---

## 📈 Stock Recommendation Logic

| Trend | Stock Action |
|------|--------------|
| Increasing | Increase Stock |
| Decreasing | Reduce Stock |
| Stable | Maintain Stock |
| Spiky | Review Data |
| Insufficient Data | Review Data |

Action strength is decided using **% deviation thresholds**.

---

## 🖥️ Streamlit Frontend

### Run the UI:

```bash
streamlit run frontend.py

Features:
✅ CSV Upload
✅ Full Agent Pipeline Execution
✅ Store Aggregation Metrics
✅ Demand Signal Report Viewer
✅ One-click Report Download

✅ **Why This Project Is Strong**
✅ Fully explainable AI system
✅ No black-box models
✅ Interview-ready architecture
✅ Pharma-compliant logic
✅ Production-style pipeline
✅ Deterministic agent collaboration
✅ UI + Backend + Data Pipeline in one project

Author - Dhiraj Athreya - https://github.com/dhirajathreya96-gif
