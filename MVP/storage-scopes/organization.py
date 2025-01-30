from google.cloud import storage
from google.api_core import page_iterator
def create_district(name, uniqueID):
    client = storage.Client()
    bucket = client.bucket(name + "_" + uniqueID)
    bucket.storage_class = "NEARLINE"
    
    new = client.create_bucket(bucket, location="us")

def remove_district(name):
    client = storage.Client()
    bucket = client.get_bucket(name)
    bucket.delete()

def list_teachers(district, school):

    extra_params = {
        "projection": "noAcl",
        "delimiter": '/'
    }

    gcs = storage.Client()
    
    path = f"/b/{district}/o"

    iterator = page_iterator.HTTPIterator(
        client=gcs,
        api_request=gcs._connection.api_request,
        path=path,
        items_key='prefixes',
        item_to_value=lambda _, item: item.rstrip('/').split('/')[-1],
        extra_params=extra_params,
    )

    return [school for school in iterator if school]