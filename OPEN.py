import streamlit as st
import pandas as pd
import psycopg2
from openai import OpenAI
import plotly.express as px
import time
import json
import os

# Set page config at the very beginning
st.set_page_config(page_title="Advanced Invoice Data Analyzer", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client(api_key):
    return OpenAI(api_key=api_key)

# Get API key from user
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    if not api_key:
        st.error("Please enter a valid OpenAI API key to proceed.")
        st.stop()

client = get_openai_client(api_key)

# Database connection
def get_db_connection(password):
    conn = psycopg2.connect(
        dbname="invoice_db",
        user="postgres",
        password=password,
        host="localhost"
    )
    return conn

# Get database password from user
db_password = os.getenv('DB_PASSWORD')
if not db_password:
    db_password = st.text_input("Enter your database password:", type="password")
    if not db_password:
        st.error("Please enter a valid database password to proceed.")
        st.stop()

# Function to execute SQL query
def execute_query(query):
    conn = get_db_connection(db_password)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to generate SQL query
def generate_sql_query(user_input, conversation_history):
    context = """
    You are an AI assistant specializing in SQL and data analysis. You're interfacing with a PostgreSQL database containing invoice data. The schema is:
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

        BRANCHES ||--o{ INVOICES : "has"
        CUSTOMERS ||--o{ INVOICES : "places"
        INVOICES ||--|{ INVOICE_ITEMS : "contains"
        PRODUCTS ||--o{ INVOICE_ITEMS : "included_in"

    Generate a SQL query to answer the user's question. Ensure your query is efficient and uses appropriate joins where necessary. If the user's question cannot be answered with the available data, explain why.
    """

    # Prepare the conversation history
    conversation = "\n".join(conversation_history[-10:])  # Get the last 10 messages

    # Prepare the messages for the API call
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates SQL queries and analyzes data."},
        {"role": "user", "content": context},
        {"role": "user", "content": f"Previous conversation:\n{conversation}\n\nUser's question: {user_input}\n\nRespond with a JSON object containing:\n1. 'sql_query': The generated SQL query\n2. 'explanation': A brief explanation of what the query does\n3. 'visualization_type': Suggest an appropriate visualization type for the data (e.g., 'bar', 'line', 'scatter', 'pie', or 'none')"}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        # If the response is not valid JSON, return a default response
        return {
            "sql_query": "SELECT 'Error: Could not generate query' as message",
            "explanation": "There was an error generating the SQL query. Please try rephrasing your question.",
            "visualization_type": "none"
        }

# Function to explain results
def explain_results(query, results):
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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes data and provides insights."},
            {"role": "user", "content": context}
        ]
    )

    return response.choices[0].message.content

# Streamlit UI
st.title("Advanced Invoice Data Analyzer")

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# User input
user_input = st.text_input("Ask a question about the invoice data:", key="user_input")

# Inside the 'Analyze' button callback:
if st.button("Analyze"):
    if user_input:
        with st.spinner("Analyzing your request..."):
            # Generate SQL query
            response = generate_sql_query(user_input, st.session_state.conversation_history)
            
            generated_query = response['sql_query']
            query_explanation = response['explanation']
            viz_type = response['visualization_type']

            # Display generated query and explanation
            st.subheader("Generated SQL Query:")
            st.code(generated_query, language="sql")
            st.write(query_explanation)

            try:
                # Execute the query with a progress bar
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                result = execute_query(generated_query)

                # Display the result
                st.subheader("Query Result:")
                st.dataframe(result)

                # Visualize the data
                if viz_type != 'none' and not result.empty:
                    st.subheader("Data Visualization:")
                    fig = None
                    if viz_type == 'bar':
                        fig = px.bar(result)
                    elif viz_type == 'line':
                        fig = px.line(result)
                    elif viz_type == 'scatter':
                        fig = px.scatter(result)
                    elif viz_type == 'pie':
                        fig = px.pie(result)
                    
                    if fig:
                        st.plotly_chart(fig)

                # Generate and display explanation
                explanation = explain_results(generated_query, result)
                st.subheader("Analysis:")
                st.write(explanation)

                # Update conversation history
                st.session_state.conversation_history.append(f"User: {user_input}")
                st.session_state.conversation_history.append(f"AI: Generated query: {generated_query}")
                st.session_state.conversation_history.append(f"AI: Analysis: {explanation}")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Display conversation history
st.sidebar.subheader("Conversation History")
for message in st.session_state.conversation_history:
    st.sidebar.write(message)

# Clear conversation history
if st.sidebar.button("Clear History"):
    st.session_state.conversation_history = []
    st.experimental_rerun()