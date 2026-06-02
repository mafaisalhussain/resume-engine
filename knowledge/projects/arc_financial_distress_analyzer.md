# ARC Financial Distress Analyzer

## Domain
Financial Analytics | Machine Learning | Risk Classification | Business Intelligence | Data Engineering

## Technologies
Python 3.11, LightGBM, XGBoost, Random Forest, Gradient Boosting, Logistic Regression, SEC EDGAR XBRL API, FastAPI, Uvicorn, Pandas, NumPy, Scikit-learn, SMOTE (imbalanced-learn), SHAP (TreeExplainer), Platt Scaling, Tableau Public

## Concepts
Financial Distress Prediction, Feature Engineering, Class Imbalance Handling, Temporal Train/Test Split, Model Calibration, Explainable AI, REST API Deployment, Interactive Data Visualization, Stakeholder Reporting

## Project Overview

End-to-end financial distress prediction system analyzing U.S. publicly listed companies via live SEC EDGAR 10-K annual filings. Predicts distress probability for any U.S.-listed company using 35 engineered financial features scored through a calibrated LightGBM classifier — achieving **0.88 AUC-ROC**, a **14% improvement** over the Altman Z-Score baseline (~0.77).

## Key Results

| Metric | Value |
|---|---|
| Companies Analyzed | 118 |
| Distressed Companies | 50 |
| Healthy Companies | 68 |
| Features Engineered | 35 |
| Best Model | LightGBM |
| AUC-ROC Score | **0.88** |
| Altman Z-Score Baseline AUC | ~0.77 |
| Improvement over Baseline | **+14%** |

## Feature Engineering

35 features across 5 categories:

| Category | Features |
|---|---|
| Core Ratios | Debt ratio, equity ratio, ROA, current ratio, net profit margin |
| Altman Z Components | Z_X1 through Z_X5, Altman Z score, adjusted Z score |
| Cash Flow | Operating CF ratio, cash vs income ratio, cash quality score |
| Temporal Trends | 1yr and 2yr changes for debt ratio, ROA, Altman Z, revenues |
| Flag Features | Buyback detection flag, growth company flag, net income positive |

## ML Pipeline Details

**Class Imbalance:** SMOTE applied to balance distressed vs. healthy company classes before training.

**Temporal Split:** Train/test split enforced by fiscal year (pre-2020 train, post-2020 test) to prevent data leakage.

**Calibration:** Platt scaling applied to LightGBM output for well-calibrated probability estimates.

**Explainability:** SHAP TreeExplainer generates feature importance rankings and per-company prediction explanations.

## Model Performance

| Model | AUC-ROC |
|---|---|
| **LightGBM** | **0.88** |
| Gradient Boosting | 0.8865 |
| Random Forest | 0.8799 |
| Logistic Regression | 0.7701 |
| Altman Z-Score (Baseline) | ~0.77 |

## Tableau Dashboard

Three-dashboard interactive story on Tableau Public:

| Story Point | Dashboard | Contents |
|---|---|---|
| 1 | Project Overview | Class balance, risk distribution, top risk companies table |
| 2 | Data Analysis (EDA) | Altman Z distribution, debt ratio trends, sector heatmap |
| 3 | Model Evaluation | Model comparison, feature importance, SHAP summary, risk scatter |

Interactive filters by Sector, Class Label, Fiscal Year; color-coded risk zones (Critical / High / Elevated / Moderate / Low); 10 connected CSV sources.

## REST API

FastAPI backend: `POST /api/v1/analyze` → live financial distress scoring for any U.S.-listed company.
