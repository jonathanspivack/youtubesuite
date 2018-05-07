import pymongo
import time


client = pymongo.MongoClient(connect=False)
db = client.youtube



def search_cache(url):
    print('searching db')
    from_mongo = db.cached.find_one({"url":url})

    if from_mongo:
        print("found in db")
        print(from_mongo['url'])
        print(from_mongo['lasttimestamp'])
        return from_mongo['lasttimestamp'], from_mongo['captionsd']
    else:
        print("need to run selenium")

    return False,False
