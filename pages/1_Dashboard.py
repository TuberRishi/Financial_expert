import streamlit as st

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("Dashboard")

# Load and display the HTML file
with open("dashboard.html", 'r', encoding='utf-8') as f:
    html = f.read()

st.components.v1.html(html, height=1100, scrolling=True)