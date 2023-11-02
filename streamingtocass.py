import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StringType
from pyspark.sql import CassandraConnector
import random
import datetime

# Initialize a Spark session:
spark = SparkSession.builder \
    .appName('KafkaCassandraIntegration') \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.4') \
    .getOrCreate()

# Cassandra connection settings
cassandra_host = "localhost"  
cassandra_port = "9042"  
keyspace = "userks"  
table_name = "userdata"  

# Read data from Kafka topic and specify the deserialization format (convert value to string):
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "user_data") \
    .load()

# Deserialize the message value from Kafka (assuming it's in string format):
kafka_stream = kafka_df.selectExpr("CAST(value AS STRING)")

# Define a user-defined function (UDF) to transform the data
def transform_data(data):
    parts = data.split(',')
    
    # Check if the data is in the expected format before unpacking
    if len(parts) == 5:
        first_name, last_name, age, date, country = parts

        # Uppercase the last name
        last_name = last_name.upper()

        # Replace age if it's over 100 or under 10 with a random age between 15 and 70
        if int(age) > 100 or int(age) < 10:
            age = str(random.randint(15, 70))

        # Parse and reformat the date
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y/%m/%d')

        # No need for the country abbreviation logic

        return (first_name, last_name, age, formatted_date, country)
    else:
        # Handle unexpected data here, such as logging or discarding the record
        return None

# Register the UDF
transform_data_udf = udf(transform_data, StringType())

# Apply the transformation to the data
transformed_df = kafka_stream.withColumn("value", transform_data_udf(col("value")))

# Filter out records where the data did not match the expected format
filtered_df = transformed_df.filter(col("value").isNotNull())

# Define the Cassandra connector
cassandra_connector = CassandraConnector(host=cassandra_host, port=cassandra_port)

# Write the transformed data to Cassandra
query = filtered_df.writeStream \
    .outputMode("append") \
    .foreachBatch(lambda batch_df, batch_id: batch_df.write \
        .format("org.apache.spark.sql.cassandra") \
        .mode("append") \
        .options(table=table_name, keyspace=keyspace) \
        .save()) \
    .start()

# Start the streaming query
query.awaitTermination()
