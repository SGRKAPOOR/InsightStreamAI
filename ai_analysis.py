# ai_analysis.py
import streamlit as st
import json
import pandas as pd
import numpy as np
import plotly.express as px

def ensure_dataframe(result):
    if isinstance(result, pd.DataFrame):
        return result
    elif isinstance(result, pd.Series):
        return result.to_frame()
    elif isinstance(result, (np.number, np.float64, np.int64, float, int)):
        return pd.DataFrame({'result': [result]})
    elif isinstance(result, (list, np.ndarray)):
        return pd.DataFrame({'result': result})
    else:
        return pd.DataFrame({'result': [result]})

def generate_advanced_analysis(client, user_input, df):
    system_message = """You are an advanced AI data analyst specializing in invoice and sales data analysis. Provide in-depth, insightful analysis based on the user's questions. Always include Python code that creates a 'result' variable with the analyzed data, and suggest an appropriate visualization. Ensure that 'result' is always a pandas DataFrame or Series, not a single value. If the analysis produces a single value, wrap it in a DataFrame with an appropriate column name."""

    user_message = f"""Analyze this invoice data:
    Columns: {', '.join(df.columns)}
    Data types: {df.dtypes.to_string()}
    Sample data:
    {df.head().to_string()}
    
    User question: {user_input}

    Provide your response in the following JSON format:
    {{
        "interpretation": "Your interpretation of the user's question",
        "code": "pandas code here that creates a 'result' variable",
        "explanation": "detailed explanation here",
        "visualization": "suggested visualization type (bar, line, scatter, or pie)",
        "insights": "comprehensive insights here",
        "recommendations": "actionable business recommendations",
        "follow_up": "suggested follow-up analyses or questions"
    }}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error in generating analysis: {str(e)}")
        return None

def safe_execute_code(code_snippet, df):
    local_vars = {"df": df, "pd": pd, "np": np}
    try:
        exec(code_snippet, globals(), local_vars)
        result = local_vars.get('result', None)
        if result is not None:
            return ensure_dataframe(result), ""
        else:
            return None, "No result variable found in executed code."
    except Exception as e:
        return None, f"Error: {str(e)}"

def create_visualization(df, viz_type, result):
    try:
        result = ensure_dataframe(result)  # Ensure result is a DataFrame
        if result.empty:
            return None

        if viz_type == 'bar':
            if len(result.columns) == 1:
                return px.bar(result, x=result.index, y=result.columns[0])
            else:
                return px.bar(result)
        elif viz_type == 'line':
            if len(result.columns) == 1:
                return px.line(result, x=result.index, y=result.columns[0])
            else:
                return px.line(result)
        elif viz_type == 'scatter':
            if len(result.columns) == 1:
                return px.scatter(result, x=result.index, y=result.columns[0])
            else:
                return px.scatter(result)
        elif viz_type == 'pie':
            if len(result.columns) == 1:
                return px.pie(result, values=result.columns[0], names=result.index)
            else:
                return px.pie(result)
        else:
            return px.bar(result)  # Default to bar chart if type is not recognized
    except Exception as e:
        st.warning(f"Could not create visualization: {str(e)}")
        return None