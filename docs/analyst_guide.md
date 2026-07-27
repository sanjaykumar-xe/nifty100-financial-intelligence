\# Nifty100 Financial Intelligence Platform

\## Analyst Guide



\## Overview



The Nifty100 Financial Intelligence Platform is an AI-powered stock analysis system built for analysing Indian listed companies.



The platform provides



\- Financial Ratio Analysis

\- CAGR Analysis

\- Cashflow Intelligence

\- Quality Ranking

\- Growth Ranking

\- Value Ranking

\- Compounder Ranking

\- Portfolio Builder

\- Portfolio Risk Analysis

\- Sector Allocation Analysis

\- Strategy Backtesting

\- Portfolio Recommendation Engine

\- Streamlit Dashboard

\- FastAPI APIs



\---



\## Workflow



Raw Excel Files

↓



SQLite Database



↓



Financial KPI Engine



↓



Ranking Engine



↓



Portfolio Builder



↓



Risk Analysis



↓



Strategy Backtesting



↓



Recommendation Engine



↓



Dashboard



↓



Reports



\---



\## Outputs



The project automatically generates



\- Company Rankings

\- Sector Reports

\- Portfolio Reports

\- Company Tearsheets

\- Risk Reports

\- Recommendation Reports



\---



\## Dashboard



Run



streamlit run src/dashboard/app.py



\---



\## API



Run



uvicorn src.api.main:app --reload



Swagger



http://127.0.0.1:8000/docs



\---



\## Testing



Run



pytest -v



All tests must pass before deployment.



\---



\## Database



Database



db/nifty100.db



Contains



\- Companies

\- Balance Sheet

\- Profit \& Loss

\- Cashflow

\- Financial Ratios



\---



\## Author



Sanjay Kumar



Artificial Intelligence \& Data Science



Ramco Institute of Technology

