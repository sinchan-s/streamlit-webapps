import os, io, time, re
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
# hide_default_format = """
#        <style>
#        #MainMenu {visibility: hidden;}
#        footer {visibility: hidden;}
#        header {visibility: hidden;}
#        </style>
#        """
# st.markdown(hide_default_format, unsafe_allow_html=True)


#! title & global variables
st.title('QA Reports')
del_pass = st.secrets["DEL_PASS"]

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
    drive = deta.Drive("qa_reports")
    return drive

conn = load_data()
qa_dash_drive = conn

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

col_sum_half = lambda df, col : (df.loc[:,col].sum()/2).round(2)

#*----------------------------------------------------------------------------*#
#*                               Sidebar content                              *#
#*----------------------------------------------------------------------------*#
drive_files_list = drive_list()

with st.sidebar:
    qa_dash_drive_files = st.multiselect('Select files:', drive_files_list, default=drive_files_list[0])    #?==> select to preview uploaded files
    user_file = st.file_uploader("Choose a file", accept_multiple_files=False, type=['csv','xls', 'xlsx'], help="**Follow this naming convention for upload: 'qa/lab/insp-<month><year>.xlsx'**")
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
            qa_dash_drive.delete(qa_dash_drive_files[0])
            st.success(f"{qa_dash_drive_files[0]} succesfully deleted!")
    if st.button(label='Refresh'):
        st.rerun()

#*----------------------------------------------------------------------------*#
#*                                  Tabs Area                                 *#
#*----------------------------------------------------------------------------*#
#! Tab-1
if selected=='Grouping':

    #!----retrieve data file
    qa_file_list = [item for item in drive_files_list if re.findall('qa-',item)]
    qa_file_select = st.multiselect('Select files:', qa_file_list, default=qa_file_list[-1], key=12)
    for i,d in enumerate(qa_file_select):
        df_full = pd.read_excel(drive_fetch(d).read(), sheet_name=None)

    with st.expander('File Preview', expanded=False):
        st.write(df_full['Summary'])
        # st.write(df_full)
    #!-----columnized file data display
    col1, col2, col3 = st.columns(3, gap='large')
    delta_val1, delta_val2, delta_val3 = 0, 0, 0
    print_vals, yd_vals = {}, {}    
    for i,d in enumerate(qa_file_select):
        df_summ = df_full['Summary']
        df_month = d.split('.')[0].split('-')[1].upper()
        p_prod = df_summ.iloc[5,3]
        p_q3 = df_summ.iloc[17:20,6].sum()+df_summ.iloc[21,6]
        yd_prod = df_summ.iloc[5,7]
        yd_q3 = df_summ.iloc[25,6]+df_summ.iloc[26,6]
        total_prod = p_prod + yd_prod
        delta_val1 = (total_prod - delta_val1)*100/delta_val1 if delta_val1 != 0 else 0
        delta_val2 = (p_prod - delta_val2)*100/delta_val2 if delta_val2 != 0 else 0
        delta_val3 = (yd_prod - delta_val3)*100/delta_val3 if delta_val3 != 0 else 0
        col1.metric(f":blue[Total Production] : :grey[{df_month}]", f"{total_prod:,.2f} m", delta=f'{delta_val1:#.1f} %')
        delta_val1 = total_prod
        col2.metric(f":orange[Print Production] : :grey[{df_month}]", f"{p_prod:,.2f} m", delta=f'{delta_val2:.1f} %')
        delta_val2 = p_prod
        col3.metric(f":violet[YD Production] : :grey[{df_month}]", f"{yd_prod:,.2f} m", delta=f'{delta_val3:.1f} %')
        delta_val3 = yd_prod
        col2.metric(f":red[Print Q3] : :grey[{df_month}]", f"{p_q3*100:,.2f} %")
        col3.metric(f":red[YD Q3] : :grey[{df_month}]", f"{yd_q3*100:,.2f} %")
        col1.bar_chart(pd.DataFrame([total_prod, p_prod, yd_prod]))


if selected=='Lab':
    #!----upload data file
    pass
    
if selected=='Inspection':
    #!----upload data file
    pass
