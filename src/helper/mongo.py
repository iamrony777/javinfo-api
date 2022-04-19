from motor import motor_asyncio
import asyncio
import os

cluster = motor_asyncio.AsyncIOMotorClient(os.environ['MONGODB_URL']) # Connection to cluster
cluster.get_io_loop = asyncio.get_running_loop
db_name = os.environ['DB_NAME']


async def insert_log(log, app):
    collection = cluster[db_name][f'{app}-logs']
    await collection.insert_one(log)
    
    return 

