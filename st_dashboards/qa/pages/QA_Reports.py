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
    drive = deta.Drive("qa_reports")
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

col_sum_half = lambda df, col : (df.iloc[:,col].sum()/2).round(2)

#*----------------------------------------------------------------------------*#
#*                               Sidebar content                              *#
#*----------------------------------------------------------------------------*#
with st.sidebar:
    st.caption("*Follow this naming convention for uploading: 'qa/lab/insp-<month><year>.xlsx'*")
    user_file = st.file_uploader("Choose a file", accept_multiple_files=False, type=['csv','xls', 'xlsx'], help="")
    upload_btn = st.button(label='Upload')
    if upload_btn:
        upld_bar = st.progress(0)   #?==> upload progress=0%
        drive_upload(user_file)
        st.success("DataFile Uploaded successfully !!")
        upld_bar.progress(100)      #?==> upload progress=100%
        time.sleep(1)
        upld_bar.empty()
    if st.toggle('More Options:'):
        st.write('Delete uploaded file:')
        del_pass = st.secrets["DEL_PASS"]
        input_pass = st.text_input('Enter Password to delete data:')
        del_disabled_status = True
        if input_pass==del_pass:    #? getting delete access
            del_disabled_status = False
        delete_button = st.button(label='Delete', disabled=del_disabled_status, use_container_width=True)
        if delete_button:
            prog_bar = st.progress(0) #?progress=0%
            qa_dash_drive.delete(qa_files[0])
            prog_bar.progress(100) #?progress=100%
            time.sleep(1)
            prog_bar.empty()
#*----------------------------------------------------------------------------*#
#*                                  Tabs Area                                 *#
#*----------------------------------------------------------------------------*#
#! Tab-1
if selected=='Grouping':
    qa_files = st.multiselect('Select files:', drive_list(), default=drive_list()[0])    #?==> select to preview uploaded files


    #!----retrieve data file
    matches = [re.findall('[q]',item) for item in drive_list()]
    st.caption(matches)
    with st.expander('File Preview', expanded=False):
        for df in qa_files:
            df_p = pd.read_excel(drive_fetch(df).read(), sheet_name='Data', skiprows=[0], index_col=0)
        t_view = st.toggle('Transpose view')
        # if t_view:
        #     st.dataframe(df_p.T)
        # else:
        #     st.dataframe(df_p)

    comparo_prog = st.progress(0, text='Comparing. Please wait...')

    #!-----columnized file data display
    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        delta_val = 0
        for i,d in enumerate(qa_files):
            comparo_prog.progress(i+10, text='Comparing. Please wait...')
            d_file = drive_fetch(d)
            df_l = pd.read_excel(d_file.read(), sheet_name='Data', skiprows=[0], index_col=0)
            tot_prod = col_sum_half(df_l,8)+col_sum_half(df_l,14)
            delta_val = (tot_prod - delta_val)*100/delta_val if delta_val != 0 else 0
            st.metric(f":blue[Total Production] : :grey[{d.split('.')[0].split('-')[1].upper()}]", f"{tot_prod:,} m", delta=f'{delta_val:#.1f} %')
            delta_val = tot_prod
        comparo_prog.progress(25, text='Comparing. Please wait...')
    with col2:
        delta_val = 0
        print_vals = {}
        for i,d in enumerate(qa_files):
            comparo_prog.progress(i+25, text='Comparing. Please wait...')
            d_file = drive_fetch(d)
            df_l = pd.read_excel(d_file.read(), sheet_name='Data', skiprows=[0], index_col=0)
            p_prod = col_sum_half(df_l,8)
            delta_val = (p_prod - delta_val)*100/delta_val if delta_val != 0 else 0
            st.metric(f":orange[Print Production] : :grey[{d.split('.')[0].split('-')[1].upper()}]", f"{p_prod:,} m", delta=f'{delta_val:#.1f} %')
            delta_val = p_prod
            print_vals[d.split('.')[0].split('-')[1].upper()] = [col_sum_half(df_l, n) for n in range(8)]
        comparo_prog.progress(63, text='Comparing. Please wait...')
        t_view = st.toggle('Transpose view', key=2)
        if t_view:
            print_chrt = pd.DataFrame(data=print_vals, index=[df_l.columns[i] for i in range(8)]).T
        else:
            print_chrt = pd.DataFrame(data=print_vals, index=[df_l.columns[i] for i in range(8)])
        st.dataframe(print_chrt)
        col_sel = st.selectbox("Choose param", range(8))
        st.bar_chart(print_chrt.iloc[col_sel, :])
    with col3:
        delta_val = 0
        yd_vals = {}
        for i,d in enumerate(qa_files):
            comparo_prog.progress(i+63, text='Comparing. Please wait...')
            d_file = drive_fetch(d)
            df_l = pd.read_excel(d_file.read(), sheet_name='Data', skiprows=[0], index_col=0)
            yd_prod = col_sum_half(df_l,14)
            delta_val = (yd_prod - delta_val)*100/delta_val if delta_val != 0 else 0
            st.metric(f":violet[YD Production] : :grey[{d.split('.')[0].split('-')[1].upper()}]", f"{yd_prod:,} m", delta=f'{delta_val:#.1f} %')
            delta_val = yd_prod
            # annotated_text((f"{col_sum_half(df_l, 14)} m", f"YD Production ({d})"))
            yd_vals[d.split('.')[0].split('-')[1].upper()] = [col_sum_half(df_l, n) for n in range(9,14)]
        comparo_prog.progress(100)
        t_view = st.toggle('Transpose view', key=3)
        if t_view:
            yd_chrt = pd.DataFrame(data=yd_vals, index=[df_l.columns[i] for i in range(9,14)]).T
        else:
            yd_chrt = pd.DataFrame(data=yd_vals, index=[df_l.columns[i] for i in range(9,14)])
        st.dataframe(yd_chrt)
        time.sleep(1)
        comparo_prog.empty()

if selected=='Lab':
    #!----upload data file
    pass
    
if selected=='Inspection':
    #!----upload data file
    pass
    