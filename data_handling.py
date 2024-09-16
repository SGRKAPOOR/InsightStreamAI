
import streamlit as st
import pandas as pd
from services import init_google_sheets_service

@st.cache_data
def load_data(sheet_id, sheet_name):
    service = init_google_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_name).execute()
    data = result.get('values', [])
    df = pd.DataFrame(data[1:], columns=data[0])
    
    numeric_columns = ['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross margin percentage', 'gross income', 'Rating']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    return df