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
    page_title="QA Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
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
st.title('QA Dashboard')
st.subheader('All insights in one place:')

#!------------nav menu
selected = option_menu(
    menu_title=None, 
    options=['NCR', 'CUR', 'C-grade(Q3)', 'Sound Surplus(Q6)', 'Complaints'],
    icons=['asterisk', 'bookmark-x', 'backspace-reverse', 'border-all', 'clipboard-x'],
    orientation='horizontal')


#! upload & read user data
user_file = st.file_uploader("Upload a CSV file")

if user_file is None:
    # @st.cache_data
    st.warning('No File uploaded: You can still play with demo-data')
    # st.write(sns.get_dataset_names())
    df = sns.load_dataset('diamonds')
else:
    st.success('File uploaded')
    col1, col2, col3, col4 = st.columns(4)
    enco = col1.selectbox("Change CSV encoding", ['utf-8', 'ascii', 'big5', 'utf-16', 'utf-32'])
    try:
        df = pd.read_csv(user_file, encoding="ansi")
    except:
        col2.warning('Try different CSV encoding')

#! basic app settings
theme = st.radio("Choose your theme", ["light", "dark"])

#! Display PyGWalker
pyg.walk(df, env='Streamlit', dark=theme)
