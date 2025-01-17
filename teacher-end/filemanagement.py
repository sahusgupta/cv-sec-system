import streamlit as st
from os import environ
from google.cloud import firestore, storage

db = firestore.Client.from_service_account_json('sys1-8196c-firebase-adminsdk-almhn-29019bddaf.json')

def get_recording(school, teacher, course, assignment, student):
    schoolRef = db.document(school)
    if schoolRef:
        teacherRef = schoolRef.collection(teacher)
        if teacherRef:
            courseRef = teacherRef.document(course)
            if courseRef:
                assignmentRef = courseRef.collection(assignment)
                if assignmentRef:
                    studentRef = assignmentRef.document(student)
                    data = studentRef.get()
                    if data.exists:
                        return data.to_dict()['path']
                    else:
                        return ""
                else:
                    return "Assignment has not been created, or you have not enabled recording for this assignment."
            else:
                return "Course not registered. Please register it using the Canvas LTI"
        else :
            return "Teacher not registered. Please register it using the Canvas LTI"
    else:
        return "School not registered. Please visit our website"
def retrieve_from_gcs(filename, bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    recording = bucket.blob(filename + '.mp4')
    url = recording.generate_signed_url(expiration=21600)
    return url


def fetch_license(school):
    if db.collection('schools').document(school):
        data = db.collection('schools').document(school).get().to_dict()
        if 'license' in data:
            return data['license']
        else:
            return "License not found for this school. Please contact the school administrator or reach out to support @ temp@gmail.com."