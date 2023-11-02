from cassandra.cluster import Cluster
from pymongo import MongoClient
import pandas as pd

# Cassandra connection settings
cassandra_host = "localhost"  
cassandra_keyspace = "userks"  
table_name = "userdata"  

# MongoDB connection settings
mongo_host = "localhost"  
mongo_port = 27017
db_name = "userdb"  
collection_name = "usercol"  

# Connect to Cassandra
cluster = Cluster([cassandra_host])
session = cluster.connect(cassandra_keyspace)

# Perform aggregations in Cassandra
query1 = f"SELECT country, count(*) as user_count FROM {table_name} GROUP BY country"
query2 = f"SELECT AVG(age) as avg_age FROM {table_name}"
query3 = f"SELECT domain, count(*) as domain_count FROM {table_name} GROUP BY domain"

result1 = session.execute(query1)
result2 = session.execute(query2)
result3 = session.execute(query3)

# Convert Cassandra results to Pandas DataFrame
df1 = pd.DataFrame(list(result1))
df2 = pd.DataFrame(list(result2))
df3 = pd.DataFrame(list(result3))

# Connect to MongoDB
mongo_client = MongoClient(mongo_host, mongo_port)
mongo_db = mongo_client[db_name]
mongo_collection = mongo_db[collection_name]

# Save the aggregations to MongoDB
mongo_collection.insert_many(df1.to_dict('records'))
mongo_collection.insert_many(df2.to_dict('records'))
mongo_collection.insert_many(df3.to_dict('records'))

# Close Cassandra cluster and MongoDB connection
cluster.shutdown()
mongo_client.close()
