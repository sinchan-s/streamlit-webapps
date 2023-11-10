import streamlit as st
import pandas as pd
import seaborn as sns
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

#! nav menu
selected = option_menu(
    menu_title=None, 
    options=['Grouping', 'Lab', 'Inspection'],
    icons=['asterisk', 'bookmark-x', 'backspace-reverse'],
    orientation='horizontal')

if selected=='Grouping':
    #!------QA data
    df = pd.read_excel('qa-sept23.xlsx', sheet_name='Data', skiprows=[0], index_col=0)
    st.dataframe(df)

    all_cols = df.columns
    for i,t in enumerate(all_cols):
        st.write(f'Σ {t}',str(df.iloc[-1,i].round(2)),'m')
