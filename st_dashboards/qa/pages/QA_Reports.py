import os, io
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
    icons=['asterisk', 'bookmark-x', 'backspace-reverse'], 
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

drive_upload = lambda fname, fpath : qa_dash_drive.put(fname, path=fpath)

drive_list = lambda : qa_dash_drive.list()['names']

drive_fetch = lambda fname: qa_dash_drive.get(fname)
#! calculative functions
half_sum = lambda col : df[col].sum()/2

#*----------------------------------------------------------------------------*#
#*                                  Tabs Area                                 *#
#*----------------------------------------------------------------------------*#
#! Tab-1
if selected=='Grouping':
    #!------QA data
    qa_file = st.selectbox('Select file:', drive_list())
    # st.write(qa_file)
    db_file = drive_fetch(qa_file)
    df = pd.read_excel(db_file.read(), sheet_name='Data', skiprows=[0], index_col=0)
    with st.expander("Preview file"):
        st.dataframe(df)
    annotated_text(("Total Production", f"{(df.iloc[-1,8]+df.iloc[-1,14])}"))

    col1, col2 = st.columns(2, gap='large')
    with col1:
        annotated_text(("Print Production", f"{half_sum('PRINT TOTAL').round(2)}"))
        print_lst_idx = ['Printed YD Production', 'Printed P/D Yardage Production', 'Printed YD Yardage Production', 'Piece Dyed Production', 'Print FRC', 'Print RG/RS Production', 'Total Print Production']
        print_lst_vals = [half_sum('Print Yd'), half_sum('Print PD Yardage '), half_sum('Print Yd Yardage '), half_sum('Piece Dyed '), half_sum('Print FRC'), half_sum('Print RG/RS'), half_sum('Print ')]
        print_df = pd.DataFrame(print_lst_vals, index=print_lst_idx, columns=['Qty (m)'])
        st.dataframe(print_df)

    with col2:
        annotated_text(("YD Production", f"{half_sum('YD TOTAL').round(2)}"))
        yd_lst_idx = ['YD Yardage Production', 'YD FRC', 'YD RG/RS Production', 'Total YD Production']
        yd_lst_vals = [half_sum('Yarn Dyed Yardage'), half_sum('Yarn Dyed FRC'), half_sum('YD RG/RS'), half_sum('Yarn Dyed')]
        yd_df = pd.DataFrame(yd_lst_vals, index=yd_lst_idx, columns=['Qty (m)'])
        st.dataframe(yd_df)

if selected=='Lab':
    #!------Lab data
    pass
    # df2 = pd.read_excel()

if selected=='Inspection':
    pass
    #!------Inspection data
    # df2 = pd.read_excel()