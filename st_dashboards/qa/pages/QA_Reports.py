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

#! calculative functions
def half_sum(col):
    return df[col].sum()/2

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
#*                                       DETA functions                                     *#
#*------------------------------------------------------------------------------------------*#
#! ncr_db_base functions
# def upload_data(defect_type, customer, article, po_no, qty, remarks):
#     return ncr_db_base.put({"key": key, "Date": date, "Defect_type": defect_type, "Customer": customer, "Article": article, "PO": po_no, "Quantity": qty, "Remarks": remarks})

def resize_n_upload_img(image_name, image_data):
    return qa_dash_drive.put(image_name, data=img_byte_arr)

def fetch_data(key):
    return ncr_db_base.get(key)

def fetch_all_data():
    res = ncr_db_base.fetch()
    return res.items

def convert_df(df):
    return df.to_csv().encode('utf-8')


#*----------------------------------------------------------------------------*#
#*                                  Tabs Area                                 *#
#*----------------------------------------------------------------------------*#
#! Tab-1
if selected=='Grouping':
    #!------QA data
    df = pd.read_excel('qa-sept23.xlsx', sheet_name='Data', skiprows=[0], index_col=0)
    # st.dataframe(df)

    annotated_text(("Total Production", f"{(df.iloc[-1,8]+df.iloc[-1,14])}"))
    # st.write('Total Production (including PD Production): ', ().round(2), 'm')

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