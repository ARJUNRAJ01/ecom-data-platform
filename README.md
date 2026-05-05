# 🛒 E-Commerce Data Platform

An end-to-end data engineering and analytics pipeline for e-commerce insights, built using **Kafka**, **DuckDB**, **dbt**, and **Dash**.

---

## 🚀 Overview

This project simulates a real-world data platform that ingests, processes, transforms, and visualizes e-commerce data.

It demonstrates:
- Data ingestion pipeline  
- Data modeling using dbt (Silver → Gold layers)  
- Analytical queries using DuckDB  
- Interactive dashboard using Dash  

---

## 🏗️ Architecture

Kafka (Data Simulation / Streaming)  
↓  
Parquet Files (Raw Data Storage)  
↓  
DuckDB (Analytical Warehouse)  
↓  
dbt (Transformations: Silver → Gold Models)  
↓  
Dash (Interactive Dashboard)  

---

## 📁 Project Structure

ecom-data-platform/  
├── ingestion/            # Data ingestion scripts  
├── data/                 # Raw & processed data (Parquet + DuckDB)  
├── processing/dbt/       # dbt models (Silver + Gold layers)  
├── dashboard/            # Dash application  
├── logs/                 # Pipeline logs  
├── requirements.txt      # Python dependencies  
├── docker-compose.yml    # Optional container setup  
└── README.md  

---

## ⚙️ Setup Instructions

### 1. Clone the repository

git clone https://github.com/ARJUNRAJ01/ecom-data-platform.git  
cd ecom-data-platform  

### 2. Install dependencies

pip install -r requirements.txt  

---

## ▶️ Running the Pipeline

### Step 1: Run dbt models

cd processing/dbt  
dbt run  

This will create:
- Silver tables (cleaned data)  
- Gold tables (analytics-ready data)  

---

### Step 2: Run Dashboard

python dashboard/app.py  

Open in browser:  
http://localhost:8050  

---

## 📊 Dashboard Features

- 📈 Revenue overview  
- 👤 Customer 360 analytics  
- 🛍️ Product insights  
- 💳 Transaction analysis  

---

## 🧠 Data Models

### Silver Layer
- silver_transactions  
- silver_web_logs  
- silver_reviews  

### Gold Layer
- gold_customer_360  

---

## 📌 Tech Stack

- Kafka → Data simulation / streaming  
- DuckDB → Analytical database  
- dbt → Data transformation & modeling  
- Dash (Plotly) → Visualization dashboard  
- Python → Core development  

---

## 💡 Key Learnings

- End-to-end data pipeline design  
- dbt-based modular transformations  
- Analytical modeling with DuckDB  
- Building interactive dashboards  

---

## 🔮 Future Improvements

- Add Airflow for orchestration  
- Real-time Kafka integration  
- Machine learning (customer segmentation / recommendations)  
- Cloud deployment (AWS / GCP)  

