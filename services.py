import streamlit as st
from openai import OpenAI
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import Config

@st.cache_resource
def init_openai_client(api_key):
    return OpenAI(api_key=api_key)

@st.cache_resource
def init_google_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        Config.SERVICE_ACCOUNT_FILE, scopes=Config.GOOGLE_SHEETS_SCOPES)
    return build('sheets', 'v4', credentials=creds)