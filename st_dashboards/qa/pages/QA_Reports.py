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

    st.write(f'Total Production: {(df.iloc[-1,8]+df.iloc[-1,14]).round(2)}m ({df.iloc[-1,8]+df.iloc[-1,14]+df.iloc[-1,4]}m)')
    # st.write('Total Production (including PD Production): ', ().round(2), 'm')

    col1, col2 = st.columns(2, gap='large')
    with col1:
        print_lst_idx = ['Printed P/D Production', 'Printed YD Production', 'Printed P/D Yardage Production', 'Printed YD Yardage Production', 'Piece Dyed Production', 'Print FRC', 'Print RG/RS Production', 'Total Print Production']
        print_lst_vals = [df.iloc[:,0].sum()/2, df.iloc[:,1].sum()/2, df.iloc[:,2].sum()/2, df.iloc[:,3].sum()/2, df.iloc[:,4].sum()/2, df.iloc[:,7].sum()/2, df.iloc[:,5].sum()/2, df.iloc[:,8].sum()/2]
        print_df = pd.DataFrame(print_lst_vals, index=print_lst_idx, columns=['Qty (m)'])
        st.dataframe(print_df)

    with col2:
        yd_lst_idx = ['YD Production', 'YD Yardage Production', 'YD FRC', 'YD RG/RS Production', 'Total YD Production']
        yd_lst_vals = [df.iloc[:,9].sum()/2, df.iloc[:,10].sum()/2, df.iloc[:,13].sum()/2, df.iloc[:,11].sum()/2, df.iloc[:,14].sum()/2]
        yd_df = pd.DataFrame(yd_lst_vals, index=yd_lst_idx, columns=['Qty (m)'])
        st.dataframe(yd_df)
