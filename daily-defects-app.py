import calendar
import datetime

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu  #pip install streamlit-option-menu
import plotly.graph_objects as go

#! page configuration
st.set_page_config(
    page_title="Daily defects observation app",
    page_icon="▲",
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


#! set title and subtitle
st.title('Daily Defects observation app')
# st.subheader('On-the-go Data Visualizing & Analyzing')

#! image display-upload area
# file = 
col1, col2 = st.columns(2)
cam_img = col1.camera_input("Take defect image")
user_img = col2.file_uploader('OR Upload defect image')
if user_img is not None:
    st.image(cam_img.getvalue())
else:
    st.image(user_img.getvalue())