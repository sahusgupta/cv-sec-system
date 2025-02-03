from google.cloud import storage
import os

def find_exam(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def upload_exam(teacher, school, district, student, examid):
    client = storage.Client()
    bucket = client.bucket(district)
    blob = bucket.blob(f"{school}/{teacher}/" + f"{student + examid}")
    blob.upload_from_file(os.path(find_exam(f"{student + str(examid)}.mp4", "/recordings")), timeout=None, content_type="video/mp4")

def fetch_all_recordings(student, teacher, school, district):
    client = storage.Client()
    bucket = client.bucket(district)
    exams = [str(blob) for blob in client.list_blobs('district', prefix=f'{school}/{teacher}') if student in blob]
    return exams