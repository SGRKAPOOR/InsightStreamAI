import streamlit as st
import os
import time
from config import Config
from services import init_openai_client
from data_handling import load_data
from ai_analysis import generate_advanced_analysis, safe_execute_code, create_visualization

def save_looker_url():
    st.session_state.saved_looker_url = st.session_state.looker_embed_url_input

def render_sidebar():
    with st.sidebar:
        st.image("C:/Users/Sagar Kapoor/Documents/SQLLM/Capture.PNG", width=200)
        st.title("InsightStreamAI")
        
        # Navigation
        st.sidebar.title("Navigation")
        tab_options = ["Home", "Analysis", "Dashboard"]
        st.session_state.active_tab = st.sidebar.radio("Go to", tab_options)
        
        # API Configuration
        with st.expander("🔑 API Configuration", expanded=True):
            api_key = st.text_input("OpenAI API Key:", type="password", key="openai_api_key")
            if api_key:
                st.session_state.openai_client = init_openai_client(api_key)
                st.success("API Key configured successfully!")
        
        # Data Source Configuration
        with st.expander("📊 Data Source", expanded=True):
            sheet_id = st.text_input("Google Sheet ID:", key="google_sheet_id")
            sheet_name = st.text_input("Sheet Name:", key="google_sheet_name")
            
            if st.button("Connect to Sheet", key="connect_sheet_button"):
                if sheet_id and sheet_name:
                    with st.spinner("Connecting to Google Sheet..."):
                        try:
                            df = load_data(sheet_id, sheet_name)
                            st.session_state.df = df
                            st.success("Connected successfully!")
                            st.dataframe(df.head())
                        except Exception as e:
                            st.error(f"Error connecting to sheet: {str(e)}")
                else:
                    st.warning("Please enter both Sheet ID and Sheet Name.")
        
        # Looker Studio Configuration
        with st.expander("📈 Looker Studio Configuration", expanded=True):
            st.text_input("Looker Studio Embedded URL:", key="looker_embed_url_input", on_change=save_looker_url)
            if 'saved_looker_url' in st.session_state:
                st.success("Looker Studio URL saved successfully!")
        
        st.markdown("---")
        st.markdown("© 2024 InsightStreamAI")
def animate_metric(label, value, icon):
    """Display an animated metric"""
    placeholder = st.empty()
    for i in range(0, 101, 10):
        placeholder.metric(label, f"{i}%", icon)
        time.sleep(0.1)
    placeholder.metric(label, value, icon)

def render_welcome():
    st.title("Welcome to InsightStreamAI")
    st.write("Unlock the power of your data with AI-driven insights and interactive visualizations.")
    
    # Animated metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        animate_metric("Data Sources", "Google Sheets", "📊")
    with col2:
        animate_metric("Analysis Engine", "OpenAI GPT", "🧠")
    with col3:
        animate_metric("Visualization", "Interactive Charts", "📈")
    
    st.markdown("---")
    st.subheader("Get Started")
    steps = [
        "Configure your OpenAI API Key in the sidebar",
        "Connect to your Google Sheet data source",
        "Navigate to the 'Analysis' tab to start exploring your data",
        "Check out the 'Dashboard' tab for a high-level overview"
    ]
    for i, step in enumerate(steps, 1):
        st.markdown(f"{i}. {step}")
    
    # Quick start guide
    with st.expander("📚 Quick Start Guide"):
        st.markdown("""
        ### Using InsightStreamAI

        1. **Connect Your Data**
           - Open the sidebar and enter your Google Sheet ID and Sheet Name
           - Click "Connect to Sheet" to load your data

        2. **Ask Questions**
           - Go to the Analysis tab
           - Type your question in the text box
           - Our AI will analyze your data and provide insights

        3. **Explore Visualizations**
           - Check out the generated charts and graphs
           - Interact with the visualizations to dive deeper

        4. **Review Insights**
           - Read the AI-generated explanations and recommendations
           - Use the follow-up questions to continue your analysis

        5. **Dashboard Overview**
           - Visit the Dashboard tab for a high-level view of your data
        """)

def render_analysis():
    st.title("🔍 AI-Powered Data Analysis")
    if 'df' in st.session_state and 'openai_client' in st.session_state:
        st.info("💡 Ask a question about your data, and our AI will analyze it for you!")
        user_input = st.text_input("Your question:", placeholder="E.g., What are the top 5 products by total sales?")
        if user_input:
            try:
                with st.spinner("🤖 AI is analyzing your data..."):
                    response = generate_advanced_analysis(st.session_state.openai_client, user_input, st.session_state.df)
                if response:
                    st.success("Analysis complete! 🎉")
                
                    tab1, tab2, tab3 = st.tabs(["📊 Results", "💡 Insights", "🧮 Technical Details"])
                
                    with tab1:
                        st.subheader("Analysis Results")
                        st.markdown(response['explanation'])
                    
                        result, error = safe_execute_code(response['code'], st.session_state.df)
                        if result is not None:
                            st.dataframe(result, use_container_width=True)
                        
                            st.subheader("Visualization")
                            fig = create_visualization(st.session_state.df, response['visualization'], result)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("Could not create visualization for this result.")
                        else:
                            st.error(f"Error executing analysis code: {error}")
                
                    with tab2:
                        st.subheader("Additional Insights")
                        st.markdown(response['insights'])
                        st.subheader("Recommendations")
                        st.markdown(response['recommendations'])
                        st.subheader("Follow-up Questions")
                        for i, question in enumerate(response['follow_up'].split('\n'), 1):
                            if question.strip():
                                st.write(f"{i}. {question.strip()}")
                    
                    with tab3:
                        st.subheader("Technical Details")
                        st.code(response['code'], language="python")
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
    else:
        st.warning("Please connect to a Google Sheet and enter your OpenAI API Key in the sidebar to start analyzing data.")
        st.image("https://via.placeholder.com/600x300.png?text=Connect+Your+Data+to+Get+Started", use_column_width=True)

def render_dashboard():
    st.title("📊 Interactive Dashboard")
    if 'saved_looker_url' in st.session_state and st.session_state.saved_looker_url:
        st.components.v1.iframe(st.session_state.saved_looker_url, width=1500, height=800, scrolling=True)
    else:
        st.warning("Please configure the Looker Studio Embedded URL in the sidebar.")