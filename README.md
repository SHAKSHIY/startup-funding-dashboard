# 🚀 Startup Funding Analyzer

A Streamlit-powered interactive dashboard to explore and visualize startup funding trends in India. Upload your own dataset or use the default one to analyze investments by year, industry, funding type, location, and more.

## 📊 Features

- 📁 Upload your own CSV file or use the default dataset
  
- 📅 Filter funding rounds by year, industry, and funding type
  
- 📈 Interactive time-series plots (funding trends, forecasts)
  
- 🏭 Top industries, startups, and locations by funding
  
- 📌 Map of top cities receiving startup investments
  
- 💰 KPIs: Total funding, unique startups, number of rounds
  
- 🔮 Forecast funding using Prophet for the next 12 months
  
- 📥 Download filtered dataset
  
- 📉 Visualize top investors by total funding and number of rounds

## 🗂 Folder Structure

![image](https://github.com/user-attachments/assets/85afc66a-a062-42ac-94b2-0c82a727f292)

### 📦 Installation

git clone https://github.com/yourusername/startup-funding-analyzer.git

cd startup-funding-analyzer

pip install -r requirements.txt

## Run the App

streamlit run app.py

## 📁 Default Dataset
- The default dataset is located at:

scripts/output/startup_funding.csv

- Ensure this file exists or upload your own CSV with the following columns:

Date, Startup, Industry, Location, Amount, Type

## 📊 Running Analysis Scripts
- To generate investor summaries (if missing):

python scripts/analyze.py

## 🔮 Forecasting
This app uses Facebook Prophet to forecast monthly funding trends. Forecasted values for the next 12 months are shown based on current filters.

## 🛠 Tech Stack
- Streamlit

- Plotly

- Prophet

- Pandas

- Mapbox (for interactive maps)
