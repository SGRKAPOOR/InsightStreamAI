# main.py
import streamlit as st
from ui_components import render_sidebar, render_welcome, render_analysis, render_dashboard

def main():
    st.set_page_config(page_title="InsightStreamAI", layout="wide")
    
    # Initialize session state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Home"
    
    # Render sidebar (which now includes navigation)
    render_sidebar()
    
    # Main content area
    if st.session_state.active_tab == "Home":
        render_welcome()
    elif st.session_state.active_tab == "Analysis":
        render_analysis()
    elif st.session_state.active_tab == "Dashboard":
        render_dashboard()

if __name__ == "__main__":
    main()