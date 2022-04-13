import asyncio
from motor import motor_asyncio
from bson.objectid import ObjectId
import os

mongo_url = os.environ['MONGODB_URL']
cluster = motor_asyncio.AsyncIOMotorClient(mongo_url)
collection = cluster['ENV']['api-env']


async def get_env():
    document = await collection.find_one({'_id': ObjectId('624882641e02c1efa353f564')})
    document = dict(document)
    return document

async def main():
    data = asyncio.get_event_loop().run_until_complete(get_env())
    for key, value in data.items():
        if key == 'JAVDB_COOKIES' or key == 'HEADERS':
            os.environ[key] = str(value).replace("'", '"')
        else:
            continue

