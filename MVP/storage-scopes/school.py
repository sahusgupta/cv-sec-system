from google.cloud import storage_control_v2, storage
from google.api_core import page_iterator

def add_school(district, school):
    client = storage_control_v2.StorageControlClient()
    proj = client.common_project_path("_")
    bucket_path = f"{proj}/buckets/{district}"

    req = storage_control_v2.CreateFolderRequest(parent=bucket_path, folder_id=school)
    resp = client.create_folder(request=req)
    return resp

def list_teachers(district, school):
    school_prefix = f"{school}/"

    extra_params = {
        "projection": "noAcl",
        "prefix": school_prefix,
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

    return [teacher for teacher in iterator if teacher]