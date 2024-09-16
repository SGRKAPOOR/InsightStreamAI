import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from openai import OpenAI
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional
import json
import os

# Configuration
class Config:
    PAGE_TITLE = "AI SQL Assistant"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    PRIMARY_COLOR = "#4A90E2"
    SECONDARY_COLOR = "#F5A623"
    BACKGROUND_COLOR = "#F0F2F6"
    TEXT_COLOR = "#333333"
    MAX_HISTORY_LENGTH = 10
    OPENAI_MODEL = "gpt-3.5-turbo"

# Database utilities
class DatabaseManager:
    @staticmethod
    @st.cache_resource
    def get_connection(password: str):
        try:
            engine = create_engine(f'postgresql://postgres:{password}@localhost/invoice_db')
            return engine
        except SQLAlchemyError as e:
            st.error(f"Database connection error: {str(e)}")
            return None

    @staticmethod
    def execute_query(query: str, engine) -> pd.DataFrame:
        try:
            return pd.read_sql_query(query, engine)
        except SQLAlchemyError as e:
            st.error(f"Query execution error: {str(e)}")
            return pd.DataFrame()

# OpenAI utilities
class OpenAIManager:
    @staticmethod
    @st.cache_resource
    def get_client(api_key: str) -> OpenAI:
        return OpenAI(api_key=api_key)

    @staticmethod
    def generate_sql_query(client: OpenAI, user_input: str, conversation_history: list) -> Dict[str, Any]:
        schema = """
        BRANCHES {
            int id PK
            varchar name
            varchar city
        }
        CUSTOMERS {
            int id PK
            varchar type
            varchar gender
        }
        PRODUCTS {
            int id PK
            varchar name
            varchar product_line
            decimal unit_price
        }
        INVOICES {
            int id PK
            int branch_id FK
            int customer_id FK
            date date
            time time
            varchar payment_method
            decimal total
            decimal cogs
            decimal gross_margin_percentage
            decimal gross_income
            decimal rating
        }
        INVOICE_ITEMS {
            int id PK
            int invoice_id FK
            int product_id FK
            int quantity
            decimal total
            decimal tax
        }
        """

        context = f"You are an AI assistant specializing in SQL and data analysis. Database schema: {schema}"
        conversation = "\n".join(conversation_history[-Config.MAX_HISTORY_LENGTH:])
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates SQL queries and analyzes data."},
            {"role": "user", "content": context},
            {"role": "user", "content": f"Previous conversation:\n{conversation}\n\nUser's question: {user_input}\n\nRespond with a JSON object containing:\n1. 'sql_query': The generated SQL query\n2. 'explanation': A brief explanation of what the query does\n3. 'visualization_type': Suggest an appropriate visualization type for the data (e.g., 'bar', 'line', 'scatter', 'pie', or 'none')"}
        ]

        try:
            response = client.chat.completions.create(model=Config.OPENAI_MODEL, messages=messages)
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error generating SQL query: {str(e)}")
            return {
                "sql_query": "SELECT 'Error: Could not generate query' as message",
                "explanation": "There was an error generating the SQL query. Please try rephrasing your question.",
                "visualization_type": "none"
            }

    @staticmethod
    def explain_results(client: OpenAI, query: str, results: pd.DataFrame) -> str:
        context = f"""
        Given this SQL query: {query}

        And these results:
        {results.to_string()}

        Provide a comprehensive analysis of the results. Include:
        1. A summary of what the data shows
        2. Any notable trends or patterns
        3. Potential business insights or recommendations based on this data
        4. Any limitations or caveats to consider when interpreting these results

        Your explanation should be detailed yet easy to understand for non-technical stakeholders.
        """

        try:
            response = client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes data and provides insights."},
                    {"role": "user", "content": context}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error explaining results: {str(e)}")
            return "An error occurred while analyzing the results. Please try again."

# Visualization utilities
class Visualizer:
    @staticmethod
    def create_visualization(df: pd.DataFrame, viz_type: str) -> Optional[go.Figure]:
        try:
            if df.empty:
                return None

            if viz_type == 'bar':
                if len(df.columns) >= 2:
                    fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                else:
                    fig = px.bar(df)
            elif viz_type == 'line':
                if len(df.columns) >= 2:
                    fig = px.line(df, x=df.columns[0], y=df.columns[1])
                else:
                    fig = px.line(df)
            elif viz_type == 'scatter':
                if len(df.columns) >= 2:
                    fig = px.scatter(df, x=df.columns[0], y=df.columns[1])
                else:
                    fig = px.scatter(df)
            elif viz_type == 'pie':
                if len(df.columns) >= 2:
                    fig = px.pie(df, values=df.columns[1], names=df.columns[0])
                else:
                    fig = px.pie(df)
            else:
                return None

            fig.update_layout(
                title=f"{viz_type.capitalize()} Chart",
                xaxis_title=df.columns[0] if len(df.columns) > 0 else "",
                yaxis_title=df.columns[1] if len(df.columns) > 1 else "",
            )

            return fig
        except Exception as e:
            st.error(f"Error creating visualization: {str(e)}")
            return Non

# UI Components
class UI:
    @staticmethod
    def setup_page():
        st.set_page_config(page_title=Config.PAGE_TITLE, page_icon=Config.PAGE_ICON, layout=Config.LAYOUT)
        st.markdown(f"""
            <style>
            .main .block-container {{ 
                padding-top: 1rem; 
                padding-bottom: 1rem;
                max-width: 960px;
                margin: 0 auto;
            }}
            .stApp {{
                background-color: {Config.BACKGROUND_COLOR};
                color: {Config.TEXT_COLOR};
            }}
            .stButton>button {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border-radius: 5px;
                border: none;
                padding: 0.5rem 1rem;
                font-weight: bold;
                transition: all 0.3s ease;
            }}
            .stButton>button:hover {{
                background-color: {Config.SECONDARY_COLOR};
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            h1, h2, h3 {{
                color: {Config.PRIMARY_COLOR};
            }}
            .stTextInput>div>div>input {{
                border-radius: 5px;
                border: 1px solid #E0E0E0;
                padding: 0.5rem;
            }}
            .stTextArea textarea {{
                border-radius: 5px;
                border: 1px solid #E0E0E0;
                padding: 0.5rem;
            }}
            .stDataFrame {{
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                overflow: hidden;
            }}
            </style>
            """, unsafe_allow_html=True)

    @staticmethod
    def sidebar():
        with st.sidebar:
            st.title("AI SQL Assistant")
            st.markdown("---")
            
            with st.expander("Settings", expanded=True):
                api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
                db_password = st.text_input("Database Password", type="password", help="Enter your database password")
            
            st.markdown("---")
            st.markdown("### How to use:")
            st.markdown("1. Enter your API key and database password")
            st.markdown("2. Type your question in natural language")
            st.markdown("3. Click 'Analyze' to get insights")

        return api_key, db_password

    @staticmethod
    def main_page():
        st.title("AI SQL Assistant")
        st.write("Ask questions about your data using natural language.")
        
        user_input = st.text_area(
            "Enter your question:",
            height=100,
            placeholder="e.g., What were the total sales for each product category last month?",
            help="Type your question here and click 'Analyze' to get insights from your data."
        )
        
        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            analyze_button = st.button("Analyze", use_container_width=True)
        with col2:
            clear_button = st.button("Clear", use_container_width=True)
        
        return user_input, analyze_button, clear_button

    @staticmethod
    def display_results(query: str, explanation: str, result: pd.DataFrame, viz: Optional[go.Figure], analysis: str):
        with st.expander("Generated SQL Query", expanded=True):
            st.code(query, language="sql")
            st.write(explanation)

        st.subheader("Query Result")
        st.dataframe(result, use_container_width=True)

        if viz:
            st.subheader("Data Visualization")
            st.plotly_chart(viz, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No visualization available for this query result.")

        with st.expander("Detailed Analysis", expanded=True):
            st.write(analysis)

    @staticmethod
    def display_error(message: str):
        st.error(message)

    @staticmethod
    def display_warning(message: str):
        st.warning(message)

    @staticmethod
    def display_success(message: str):
        st.success(message)

# Main application logic
class AIAssistant:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.openai_manager = OpenAIManager()
        self.visualizer = Visualizer()
        self.ui = UI()

    def run(self):
        self.ui.setup_page()
        api_key, db_password = self.ui.sidebar()

        if not api_key or not db_password:
            self.ui.display_warning("Please enter your OpenAI API key and database password in the sidebar to proceed.")
            return

        openai_client = self.openai_manager.get_client(api_key)
        db_engine = self.db_manager.get_connection(db_password)

        if not db_engine:
            return

        user_input, analyze_button, clear_button = self.ui.main_page()

        if clear_button:
            st.session_state.conversation_history = []
            st.experimental_rerun()

        if analyze_button and user_input:
            self.process_query(openai_client, db_engine, user_input)
        elif analyze_button:
            self.ui.display_warning("Please enter a question before analyzing.")

    def process_query(self, openai_client: OpenAI, db_engine, user_input: str):
        conversation_history = st.session_state.get('conversation_history', [])

        with st.spinner("Analyzing your request..."):
            response = self.openai_manager.generate_sql_query(openai_client, user_input, conversation_history)

            query = response['sql_query']
            explanation = response['explanation']
            viz_type = response['visualization_type']

            result = self.db_manager.execute_query(query, db_engine)

            if result.empty:
                self.ui.display_warning("The query returned no results. Please try a different question.")
                return

            viz = self.visualizer.create_visualization(result, viz_type)

            analysis = self.openai_manager.explain_results(openai_client, query, result)

            self.ui.display_results(query, explanation, result, viz, analysis)

            # Update conversation history
            conversation_history.append(f"User: {user_input}")
            conversation_history.append(f"AI: Generated query: {query}")
            conversation_history.append(f"AI: Analysis: {analysis}")

            # Trim conversation history if it exceeds the maximum length
            if len(conversation_history) > Config.MAX_HISTORY_LENGTH * 3:
                conversation_history = conversation_history[-Config.MAX_HISTORY_LENGTH * 3:]

            st.session_state.conversation_history = conversation_history

        self.ui.display_success("Analysis complete!")

if __name__ == "__main__":
    assistant = AIAssistant()
    assistant.run()