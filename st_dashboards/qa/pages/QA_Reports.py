import os, io, time
import streamlit as st
import pandas as pd
import seaborn as sns
from deta import Deta
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
    icons=['palette2', 'columns-gap', 'search'], 
    orientation='horizontal')

#! initialize deta Base & Drive
def load_data():
    DETA_KEY = st.secrets["DETA_KEY"]
    deta = Deta(DETA_KEY)
    db = deta.Base("ncr_db")
    drive = deta.Drive("qa_dash")
    return db, drive

conn = load_data()
ncr_db_base = conn[0]
qa_dash_drive = conn[1]

#*------------------------------------------------------------------------------------------*#
#*                                        Functions                                         *#
#*------------------------------------------------------------------------------------------*#
#! ncr_db_base functions
db_upload = lambda details : ncr_db.put({"key": str(datetime.now().timestamp()), "date": datetime.now().strftime("%m/%d/%Y"), "time": datetime.now().strftime("%H:%M:%S"), "details": details})

db_fetch = lambda key : ncr_db.get(key)

db_fetch_all = lambda : ncr_db.fetch().items

drive_upload = lambda file : qa_dash_drive.put(file.name, data=file)

drive_list = lambda : qa_dash_drive.list()['names']

drive_fetch = lambda fname: qa_dash_drive.get(fname)
#! calculative functions
col_sum_half = lambda df, col : (df.iloc[:,col].sum()/2).round(2)

#*----------------------------------------------------------------------------*#
#*                                  Tabs Area                                 *#
#*----------------------------------------------------------------------------*#
#! Tab-1
if selected=='Grouping':
    #!----upload data file
    with st.expander(":arrow_up_small: Upload data file"):
        user_file = st.file_uploader("", accept_multiple_files=False, type=['csv','xls', 'xlsx'], help="")
        upload_btn = st.button(label='Upload')
        st.caption("*Naming convention for uploading is 'qa-<month_name><year>.xlsx', e.g.: 'qa-nov23.xlsx'")
        if upload_btn:
            prog_bar = st.progress(0) #?==> upload progress=0%
            drive_upload(user_file)
            st.success("DataFile Uploaded successfully !!")
            prog_bar.progress(100) #?==> upload progress=100%

    #!----retrieve data file
    qa_file = st.selectbox('Select file:', drive_list())                                #?==> select to preview uploaded files
    comparo = st.toggle('Compare All files')
    comparo_prog = st.progress(0)
    drive_file = drive_fetch(qa_file)                                                      #?==> fetching selected file
    df = pd.read_excel(drive_file.read(), sheet_name='Data', skiprows=[0], index_col=0)    #?==> reading file
    df_cols = df.columns
    with st.expander("Preview file"):
        st.dataframe(df)

    #!-----columnized file data display
    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        if comparo:
            for i,d in enumerate(drive_list()):
                comparo_prog.progress(i+10)
                d_file = drive_fetch(d)
                df_l = pd.read_excel(d_file.read(), sheet_name='Data', skiprows=[0], index_col=0)
                annotated_text((f"{col_sum_half(df_l,8)+col_sum_half(df_l,14)} m", f"Total Production ({d})"))
            comparo_prog.progress(25)
        else:
            annotated_text((f"{col_sum_half(df,8)+col_sum_half(df,14)} m", "Total Production (Print+YD)"))
    with col2:
        print_vals = {}
        if comparo:
            for i,d in enumerate(drive_list()):
                comparo_prog.progress(i+25)
                d_file = drive_fetch(d)
                df_l = pd.read_excel(d_file.read(), sheet_name='Data', skiprows=[0], index_col=0)
                annotated_text((f"{col_sum_half(df_l, 8)} m", f"Print Production ({d})"))
                print_vals[d] = [str(col_sum_half(df_l, n))+' m' for n in range(8)]
            comparo_prog.progress(63)
        else:
            annotated_text((f"{col_sum_half(df, 8)} m", f"Print Production (Total)"))
            print_vals['Qty'] = [str(col_sum_half(df, n))+' m' for n in range(8)]
        st.dataframe(pd.DataFrame(data=print_vals, index=[df_cols[i] for i in range(8)]))
    with col3:
        yd_vals = {}
        if comparo:
            for i,d in enumerate(drive_list()):
                comparo_prog.progress(i+63)
                d_file = drive_fetch(d)
                df_l = pd.read_excel(d_file.read(), sheet_name='Data', skiprows=[0], index_col=0)
                annotated_text((f"{col_sum_half(df_l, 14)} m", f"YD Production ({d})"))
                yd_vals[d] = [str(col_sum_half(df_l, n))+' m' for n in range(9,14)]
            comparo_prog.progress(100)
        else:
            annotated_text((f"{col_sum_half(df, 14)} m", f"YD Production (Total)"))
            yd_vals['Qty'] = [str(col_sum_half(df, n))+' m' for n in range(9,14)]
        st.dataframe(pd.DataFrame(data=yd_vals, index=[df_cols[i] for i in range(9,14)]))
        time.sleep(1)
        comparo_prog.empty()
if selected=='Lab':
    #!------Lab data
    pass
    # df2 = pd.read_excel()

if selected=='Inspection':
    pass
    #!------Inspection data
    # df2 = pd.read_excel()