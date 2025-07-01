import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from data.fetch_data import fetch_interbank_liquidity_data
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask and Dash
server = Flask(__name__)
server.config['MONGO_URI'] = os.getenv('MONGO_URI')
server.secret_key = os.urandom(24)
mongo = PyMongo(server)
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Fetch and preprocess data
data = fetch_interbank_liquidity_data()
df = pd.DataFrame(data)
df['end_of_date'] = pd.to_datetime(df['end_of_date'])

interbank_db = mongo.cx['interbank_db']
interbank_db.liquidity.drop()
interbank_db.liquidity.insert_many(df.to_dict('records'))

available_metrics = [
    'opening_balance',
    'closing_balance',
    'forecast_aggregate_bal_t1',
    'forecast_aggregate_bal_t2',
    'forecast_aggregate_bal_t3',
    'forecast_aggregate_bal_t4',
    'forecast_aggregate_bal_u'
]

# Dash Layout
app.layout = html.Div([
    html.H1('Interbank Liquidity Dashboard', style={'textAlign': 'center', 'color': '#003366'}),
    html.A('Logout', href='/logout',
           style={'position': 'absolute', 'top': '10px', 'right': '10px', 'color': '#003366'}),
    dcc.DatePickerRange(
        id='date-picker',
        start_date=df['end_of_date'].min().date(),
        end_date=df['end_of_date'].max().date(),
        display_format='YYYY-MM-DD',
        style={'margin': '20px'}
    ),
    dcc.Dropdown(
        id='metric-selector',
        options=[{'label': col.replace('_', ' ').title(), 'value': col} for col in available_metrics],
        value='opening_balance',
        style={'width': '50%', 'margin': '0 auto'}
    ),
    dcc.Graph(id='liquidity-trend'),
    dcc.Graph(id='balance-distribution'),
    html.Div([
        html.H3('Key Metrics', style={'color': '#003366'}),
        html.P(id='total-liquidity'),
        html.P(id='avg-balance'),
        html.P(id='volatility')
    ], style={'textAlign': 'center', 'marginTop': '20px', 'color': '#003366'})
], style={'padding': '20px', 'fontFamily': 'Arial', 'color': '#003366'})


# Dash Callbacks
@app.callback(
    [Output('liquidity-trend', 'figure'),
     Output('balance-distribution', 'figure'),
     Output('total-liquidity', 'text'),
     Output('avg-balance', 'text'),
     Output('volatility', 'text')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('metric-selector', 'value')]
)
def update_dashboard(start_date, end_date, metric):
    filtered_df = df[
        (df['end_of_date'] >= pd.to_datetime(start_date)) & (df['end_of_date'] <= pd.to_datetime(end_date))]

    # Line Chart
    fig_trend = px.line(filtered_df, x='end_of_date', y=metric,
                        title=f'{metric.replace("_", " ").title()} Over Time',
                        labels={'end_of_date': 'Date', metric: 'Amount (HKD)'})
    fig_trend.update_layout(template='plotly_white', title_x=0.5, title_font_color='#003366', font_color='#003366')

    # Histogram
    fig_balance = px.histogram(filtered_df, x=metric,
                               title=f'Distribution of {metric.replace("_", " ").title()}',
                               labels={metric: 'Amount (HKD)'})
    fig_balance.update_layout(template='plotly_white', title_x=0.5, title_font_color='#003366', font_color='#003366')

    # Key Metrics
    total_liquidity = f"Total Liquidity: {filtered_df[metric].sum():,.2f} HKD"
    avg_balance = f"Average Balance: {filtered_df[metric].mean():,.2f} HKD"
    volatility = f"Volatility (Std Dev): {filtered_df[metric].std():,.2f} HKD"

    return fig_trend, fig_balance, total_liquidity, avg_balance, volatility


# Flask Routes
@server.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard/')
    return redirect(url_for('login'))


@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = interbank_db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect('/dashboard/')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@server.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if interbank_db.users.find_one({'username': username}):
            return render_template('register.html', error='Username already exists')
        hashed_password = generate_password_hash(password)
        interbank_db.users.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')


@server.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    server.run(debug=True)