import pandas as pd
from pymongo import MongoClient

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('data.csv').reset_index(drop=False).rename({'index': 'id'})
df['credit'] = df['credit'].str.replace('.', '').astype(float)
# insert data to mongodb
# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['transaction_db']
collection = db['transactions']

# Convert DataFrame to list of dictionaries
records = df.to_dict('records')

# Insert data into MongoDB
result = collection.insert_many(records)

print(f"Inserted {len(result.inserted_ids)} documents into MongoDB")

# Close the MongoDB connection
client.close()

# use transaction_db
# db.transactions.createIndex({ description: "text" })