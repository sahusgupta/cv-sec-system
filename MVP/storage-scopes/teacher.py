from google.cloud import storage, storage_control_v2

def add_teacher(district, school, teacher):
    client = storage_control_v2.StorageControlClient()
    proj = client.common_project_path("_")
    bucket_path = f"{proj}/buckets/{district}/{school}"
    req = storage_control_v2.CreateFolderRequest(parent=bucket_path, folder_id=teacher)
    resp = client.create_folder(request=req)
    return resp

def fetch_all_recordings_for_student(student, teacher, school, district):
    client = storage.Client()
    bucket = client.bucket(district)
    exams = [str(blob) for blob in client.list_blobs('district', prefix=f'{school}/{teacher}') if student in blob]
    return exams

def retrieve_all_by_exam_ID(examID, teacher, school, district):
    client = storage.Client()
    bucket = client.bucket(district)
    exams = [str(blob) for blob in client.list_blobs('district', prefix=f'{school}/{teacher}') if examID in blob]
    return exams

def download(blob_name, district):
    client = storage.Client()
    bucket = client.bucket(district)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(str(blob))
