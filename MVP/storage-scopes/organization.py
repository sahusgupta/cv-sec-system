from google.cloud import storage

def create_district(name, uniqueID):
    client = storage.Client()
    bucket = client.bucket(name + "_" + uniqueID)
    bucket.storage_class = "NEARLINE"
    new = client.create_bucket(bucket, location="us")

def remove_district(name):
    client = storage.Client()
    bucket = client.get_bucket(name)
    bucket.delete()

