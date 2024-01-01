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
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       header {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)


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
    qa_files_idx = [i for i,item in enumerate(drive_files_list) if re.findall('qa-',item)]
    qa_list = [drive_files_list[i] for i in qa_files_idx]
    qa_file_select = st.multiselect('Select files:', qa_list, default=qa_list[0], key=12)
    with st.expander('File Preview', expanded=False):
        for df in qa_file_select:
            df_p = pd.read_excel(drive_fetch(df).read(), sheet_name='Data', skiprows=[0], index_col=0)
        t_view = st.toggle('Transpose view')
        if t_view:
            st.dataframe(df_p.T)
        else:
            st.dataframe(df_p)
    comparo_prog = st.progress(0, text='Comparing. Please wait...')

    #!-----columnized file data display
    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        delta_val = 0
        for i,d in enumerate(qa_file_select):
            comparo_prog.progress(i+10, text='Comparing. Please wait...')
            d_file = drive_fetch(d)
            df_l = pd.read_excel(d_file.read(), sheet_name='Data', skiprows=[0], index_col=0)
            tot_prod = (col_sum_half(df_l,"PRINT TOTAL")+col_sum_half(df_l,"YD TOTAL")).round(2)
            delta_val = (tot_prod - delta_val)*100/delta_val if delta_val != 0 else 0
            st.metric(f":blue[Total Production] : :grey[{d.split('.')[0].split('-')[1].upper()}]", f"{tot_prod:,} m", delta=f'{delta_val:#.1f} %')
            delta_val = tot_prod
        comparo_prog.progress(25, text='Comparing. Please wait...')
    with col2:
        delta_val = 0
        print_vals = {}
        for i,d in enumerate(qa_file_select):
            comparo_prog.progress(i+25, text='Comparing. Please wait...')
            d_file = drive_fetch(d)
            df_print = pd.read_excel(d_file.read(), sheet_name='Summary')
            p_prod = df_print.iloc[5,3] #col_sum_half(df_print,"PRINT TOTAL")
            delta_val = (p_prod - delta_val)*100/delta_val if delta_val != 0 else 0
            st.metric(f":orange[Print Production] : :grey[{d.split('.')[0].split('-')[1].upper()}]", f"{p_prod:,.2f} m", delta=f'{delta_val:.1f} %')
            delta_val = p_prod
        comparo_prog.progress(63, text='Comparing. Please wait...')
        t_view = st.toggle('Transpose view', key=2)
        st.write(df_print.iloc[6:14,3])
        # print_df = pd.DataFrame(data=df_print.iloc[6,3], index=[df_print.iloc[6:14,0]])
        # if t_view:
        #     print_chrt = print_df.T
        # else:
        #     print_chrt = print_df
        # st.dataframe(print_chrt)
        # col_sel = st.selectbox("Choose param", range(8))
        # st.bar_chart(print_chrt.iloc[col_sel, :])
    with col3:
        delta_val = 0
        yd_vals = {}
        for i,d in enumerate(qa_file_select):
            comparo_prog.progress(i+63, text='Comparing. Please wait...')
            d_file = drive_fetch(d)
            df_yd = pd.read_excel(d_file.read(), sheet_name='Summary')
            yd_prod = df_yd.iloc[5,7]
            delta_val = (yd_prod - delta_val)*100/delta_val if delta_val != 0 else 0
            st.metric(f":violet[YD Production] : :grey[{d.split('.')[0].split('-')[1].upper()}]", f"{yd_prod:,.2f} m", delta=f'{delta_val:.1f} %')
            delta_val = yd_prod
            # yd_vals[d.split('.')[0].split('-')[1].upper()] = [col_sum_half(df_yd, n) for n in range(9,14)]
        comparo_prog.progress(100)
        # t_view = st.toggle('Transpose view', key=3)
        # if t_view:
        #     yd_chrt = pd.DataFrame(data=yd_vals, index=[df_yd.columns[i] for i in range(9,14)]).T
        # else:
        #     yd_chrt = pd.DataFrame(data=yd_vals, index=[df_yd.columns[i] for i in range(9,14)])
        # st.dataframe(yd_chrt)
        time.sleep(1)
        comparo_prog.empty()

if selected=='Lab':
    #!----upload data file
    pass
    
if selected=='Inspection':
    #!----upload data file
    pass
    