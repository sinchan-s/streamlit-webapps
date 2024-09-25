
#! important libraries
import os, pathlib, time
import streamlit as st
import pandas as pd
import seaborn as sns
import pygwalker as pyg
from deta import Deta
from streamlit_option_menu import option_menu  #pip install streamlit-option-menu
from annotated_text import annotated_text, annotation   #pip install st-annotated-text

#! Set page configuration
st.set_page_config(
    page_title="QA Dashboard",
    page_icon=":chart_with_downwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

#! clean streamlit styling
# hide_default_format = """
#        <style>
#        #MainMenu {visibility: hidden;}
#        footer {visibility: hidden;}
#        header {visibility: hidden;}
#        </style>
#        """
# st.markdown(hide_default_format, unsafe_allow_html=True)


#! title, subtitle & global variables
st.title('QA Dashboard')
st.subheader('All insights in one place:')
del_pass = st.secrets["DEL_PASS"]

#! nav menu
selected = option_menu(
    menu_title=None, 
    options=['NCR', 'CUR', 'Q3', 'Q6', 'Complaints'],
    icons=['asterisk', 'bookmark-x', 'backspace-reverse', 'border-all', 'clipboard-x'],
    orientation='horizontal')

#! initialize deta Base & Drive
# @st.cache_resource(ttl=3600)
def load_data():
    DETA_KEY = st.secrets["DETA_KEY"]
    deta = Deta(DETA_KEY)
    db = deta.Base("ncr_db")
    drive = deta.Drive("qa_dash")
    return db, drive

conn = load_data()
ncr_db = conn[0]
xls_drive = conn[1]

#*------------------------------------------------------------------------------------------*#
#*                                       DETA functions                                     *#
#*------------------------------------------------------------------------------------------*#
db_upload = lambda details : ncr_db.put({"key": str(datetime.now().timestamp()), "date": datetime.now().strftime("%m/%d/%Y"), "time": datetime.now().strftime("%H:%M:%S"), "details": details})

db_fetch = lambda key : ncr_db.get(key)

db_fetch_all = lambda : ncr_db.fetch().items

drive_upload = lambda file : xls_drive.put(file.name, data=file)

drive_list = lambda : xls_drive.list()['names']

drive_fetch = lambda fname: xls_drive.get(fname)

#*------------------------------------------------------------------------------------------*#
#*                                    Sidebar: upload files                                 *#
#*------------------------------------------------------------------------------------------*#
with st.sidebar:
    xls_drive_files = st.multiselect('Select files:', drive_list(), default=drive_list()[0])    #?==> select to preview uploaded files
    user_file = st.file_uploader("Choose a file", accept_multiple_files=False, type=['csv','xls', 'xlsx'], help="**Follow this naming convention for upload: 'NCR/CUR/Comp-<month><year>.xlsx'**")
    if st.button(label='Upload'):
        drive_upload(user_file)
        st.success("File uploaded successfully!!")
    if st.toggle('More Options:'):
        input_pass = st.text_input(f'Delete uploaded file (Enter Password):')
        del_disabled_status = True
        if input_pass==del_pass:    #? getting delete access
            del_disabled_status = False
        delete_button = st.button(label='Delete', disabled=del_disabled_status, use_container_width=True)
        if delete_button:
            qa_dash_drive.delete(xls_drive_files[0])
            st.success(f"{xls_drive_files[0]} succesfully deleted!")
    if st.button(label='Refresh'):
        st.rerun()

#*------------------------------------------------------------------------------------------*# 
#*                                         NAV-1: NCR                                       *#
#*------------------------------------------------------------------------------------------*#
if selected=='NCR':

    #!------------graph display
    ncr_data_list = st.selectbox("Choose data: ", xls_drive.list()['names'])
    ncr_main_chart = st.bar_chart()
    col1, col2, col3 = st.columns(3, gap="large")
    col1.write('DisplayC')
    col2.write('DisplayT')
    col3.write('DisplayI')
    ncr_chart = col1.bar_chart()
    ncr_chart2 = col2.bar_chart()
    ncr_df = st.dataframe()

#*------------------------------------------------------------------------------------------*# 
#*                                         NAV-2: CUR                                       *#
#*------------------------------------------------------------------------------------------*#
if selected=='CUR':

    #!------------graph display
    cur_data_list = st.selectbox("Choose data: ", xls_drive.list()['names'])
    st.dataframe(pd.read_excel(drive_fetch(cur_data_list).read(), sheet_name='EDPCurReport'))
    cur_main_chart = st.bar_chart()
    col1, col2, col3 = st.columns(3, gap="large")
    col1.write('DisplayC')
    col2.write('DisplayT')
    col3.write('DisplayI')
    cur_chart = col1.bar_chart()
    cur_chart3 = col3.bar_chart()
    cur_df = st.dataframe()

#*------------------------------------------------------------------------------------------*# 
#*                                         NAV-3: Q3                                        *#
#*------------------------------------------------------------------------------------------*#
if selected=='Q3':

    #!------------graph display
    q3_data_list = st.selectbox("Choose data: ", xls_drive.list()['names'])
    q3_main_chart = st.bar_chart()
    col1, col2, col3 = st.columns(3, gap="large")
    col1.write('DisplayC')
    col2.write('DisplayT')
    col3.write('DisplayI')
    q3_chart2 = col2.bar_chart()
    q3_chart3 = col3.bar_chart()
    q3_df = st.dataframe()

#*------------------------------------------------------------------------------------------*# 
#*                                         NAV-4: Q6                                        *#
#*------------------------------------------------------------------------------------------*#
if selected=='Q6':

    #!------------graph display
    q6_data_list = st.selectbox("Choose data: ", xls_drive.list()['names'])
    q6_main_chart = st.bar_chart()
    col1, col2, col3 = st.columns(3, gap="large")
    col1.write('DisplayC')
    col2.write('DisplayT')
    col3.write('DisplayI')
    q6_chart = col1.bar_chart()
    q6_df = st.dataframe()

#*------------------------------------------------------------------------------------------*# 
#*                                    NAV-5: Complaints                                     *#
#*------------------------------------------------------------------------------------------*#
if selected=='Complaints':

    #!------------graph display
    comp_data_list = st.selectbox("Choose data: ", xls_drive.list()['names'])
    comp_main_chart = st.bar_chart()
    col1, col2, col3 = st.columns(3, gap="large")
    col1.write('DisplayC')
    col2.write('DisplayT')
    col3.write('DisplayI')
    comp_chart3 = col3.bar_chart()
    comp_df = st.dataframe()

