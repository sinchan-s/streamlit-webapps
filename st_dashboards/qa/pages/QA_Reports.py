#! Code inspired from Sven Bosau @ https://github.com/Sven-Bo/PyGWalker-Guide-for-Streamlit-and-Jupyter/blob/main/app.py
import streamlit as st
import pandas as pd
import seaborn as sns
import pygwalker as pyg
import sqlite3
from streamlit_option_menu import option_menu  #pip install streamlit-option-menu
from annotated_text import annotated_text, annotation   #pip install st-annotated-text

#! Set page configuration
st.set_page_config(
    page_title="QA Reports",
    page_icon=":memo:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

#! clean streamlit styling
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       header {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

#! Set title and subtitle
st.title('QA Reports')
# st.subheader('Upload file to explore insights:')

