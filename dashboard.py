import streamlit as st
from os import environ
import firebase_admin as firebase
import google.cloud
from firebase_admin import firestore

environ.get("CRED_PATH")
creds = firebase.credentials.Certificate('sys1-8196c-firebase-adminsdk-almhn-29019bddaf.json')
st.set_page_config("Teacher View")

app = firebase.initialize_app(creds)
store = firestore.client()
