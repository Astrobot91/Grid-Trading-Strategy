import pymongo

client = pymongo.MongoClient("mongodb+srv://Astrobot91:Iavenjq9141@tradingcluster.may1xxl.mongodb.net/")

def connect_coll(db_name, coll_name):
    db = client[f"{db_name}"]
    coll = db[f"{coll_name}"]
    return coll
