# InterbankLiquidityDashboard

This project is an interactive dashboard for analyzing daily interbank liquidity data from the Hong Kong Monetary Authority (HKMA). 

## Features
- **User Authentication**: Secure registration and login system using Flask and MongoDB.
- **Data Source**: Fetches real-time data from the HKMA API.
- **Visualizations**: Interactive line charts and histograms using Plotly Dash, with date range filtering and metric selection.
- **Key Metrics**: Displays total liquidity, average balance, and volatility (standard deviation).

## Tech Stack
- **Backend**: Flask, Python, pandas, MongoDB
- **Frontend**: Plotly Dash
- **Styling**: Custom CSS

## Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Set up your MongoDB cluster and create a  .env file to include the MONGO_URL
3. Run the application: `python app.py`
4. Access the login page at `http://localhost:5000/`, register, and log in to view the dashboard at `/dashboard/`.
