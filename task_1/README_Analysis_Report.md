# Comprehensive Data Analysis Report

## Project Overview
This project delivers a comprehensive analytical framework for the provided datasets (`annex1.csv` to `annex4.csv`). The analysis focuses on extracting actionable business intelligence through rigorous data engineering, interactive visual exploration, and strategic insight generation.

## Methodology
Our approach follows the **DIKW Pyramid** (Data -> Information -> Knowledge -> Wisdom):
1.  **Data Engineering**: Robust ingestion pipelines using `pandas` to handle inconsistent formats (e.g., mixed datetime strings in sales data) and clean anomalies.
2.  **Exploratory Data Analysis (EDA)**: Utilizing **Interactive Dashboards** (powered by `plotly`) to allow stakeholders to self-serve insights (zooming, filtering, hovering).
3.  **Statistical Profiling**: Analyzing distributions, volatility (standard deviation), and Pareto patterns (80/20 rule) to identify risks and opportunities.
4.  **Strategic Recommendations**: Synthesizing visual patterns into concrete business actions (e.g., "Just-In-Time ordering for high-loss items").

## Deliverables
The analysis is modularized into 4 interactive Jupyter Notebooks:

### 1. [Product Master Data Analysis](annex1_analysis.ipynb)
*   **Dataset**: `annex1.csv`
*   **Focus**: Portfolio Structure & Data Governance.
*   **Key Viz**: Interactive Treemaps of product categories.
*   **Insight**: Portfolio rationalization opportunities for niche categories.

### 2. [Sales Transaction Analysis](annex2_analysis.ipynb)
*   **Dataset**: `annex2.csv`
*   **Focus**: Sales Trends & Operations.
*   **Key Viz**: Intraday Sales Heatmaps (Hour vs Day), Zoomable Time-series.
*   **Insight**: Workforce optimization based on "Heartbeat" analysis of store traffic.

### 3. [Wholesale Price Analysis](annex3_analysis.ipynb)
*   **Dataset**: `annex3.csv`
*   **Focus**: Cost Volatility & Inflation.
*   **Key Viz**: Volatility Radar (Bubble Chart) identifying high-risk unstable items.
*   **Insight**: Procurement strategies (Dynamic Pricing vs Fixed Contracts).

### 4. [Loss Rate Analysis](annex4_analysis.ipynb)
*   **Dataset**: `annex4.csv`
*   **Focus**: Waste Reduction & Profit Protection.
*   **Key Viz**: Pareto Charts of Top 20 "Red Zone" high-loss items.
*   **Insight**: Operational protocols for handling perishable inventory.

## How to Run
1.  Ensure you have the required libraries installed:
    ```bash
    pip install pandas plotly seaborn matplotlib
    ```
2.  Open the notebooks in Jupyter Lab or VS Code to interact with the dashboards.
