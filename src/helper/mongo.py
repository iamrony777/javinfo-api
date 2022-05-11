from motor import motor_asyncio
import asyncio
import os

cluster = motor_asyncio.AsyncIOMotorClient(os.environ['MONGODB_URL']) # Connection to cluster
cluster.get_io_loop = asyncio.get_running_loop
db_name = os.environ['DB_NAME']


async def insert_log(log, app):
    collection = cluster[db_name][f'{app}-logs']
    await collection.insert_one(log)
    

async def insert_bulk(data: list, db_name: str, collection_name: str):
    collection = cluster[db_name][collection_name]
    await collection.insert_many(data)

async def search(query: dict, db_name: str, collection_name: str):
    result = []
    collection = cluster[db_name][collection_name]
    for i in await collection.find(query).to_list(length=100):
        result.append(i)
    return result

async def drop(db_name: str, collection_name: str):
    collection = cluster[db_name]
    await collection.drop_collection(collection_name)