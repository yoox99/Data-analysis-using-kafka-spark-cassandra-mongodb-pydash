import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output
from pymongo import MongoClient
from cassandra.cluster import Cluster
import plotly.express as px

# MongoDB connection settings
mongo_host = "localhost"  
mongo_port = 27017
db_name = "userdb"  
collection_name = "usercol"  

# Cassandra connection settings
cassandra_host = "localhost"  
cassandra_keyspace = "userks"  
table_name = "userdata"  

# Connect to MongoDB
mongo_client = MongoClient(mongo_host, mongo_port)
mongo_db = mongo_client[db_name]
mongo_collection = mongo_db[collection_name]

# Connect to Cassandra
cluster = Cluster([cassandra_host])
session = cluster.connect(cassandra_keyspace)

# Create a Dash web application
app = dash.Dash(__name__)

# Define the Dash layout
app.layout = html.Div([
    html.H1("Data Aggregation Visualization"),
    dcc.Graph(id='user-count-graph'),
    dcc.Graph(id='avg-age-graph'),
    dcc.Graph(id='domain-count-graph')
])

# Callback to update the graphs
@app.callback(
    Output('user-count-graph', 'figure'),
    Output('avg-age-graph', 'figure'),
    Output('domain-count-graph', 'figure'),
    Input('user-count-graph', 'id')
)
def update_graph(_):
    # Retrieve data from MongoDB
    user_count_data = list(mongo_collection.find({"user_count": {"$exists": True}}))
    avg_age_data = list(mongo_collection.find({"avg_age": {"$exists": True}}))
    domain_count_data = list(mongo_collection.find({"domain_count": {"$exists": True}}))

    # Convert MongoDB results to Pandas DataFrames
    user_count_df = pd.DataFrame(user_count_data)
    avg_age_df = pd.DataFrame(avg_age_data)
    domain_count_df = pd.DataFrame(domain_count_data)

    # Create figures using Plotly Express
    user_count_fig = px.bar(user_count_df, x='country', y='user_count', title='User Count by Nationality')
    avg_age_fig = px.bar(avg_age_df, title='Average User Age')
    domain_count_fig = px.bar(domain_count_df, x='domain', y='domain_count', title='Common Email Domains')

    return user_count_fig, avg_age_fig, domain_count_fig

if __name__ == '__main__':
    app.run_server(debug=True)
