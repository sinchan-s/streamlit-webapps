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

    # all_cols = df.columns
    # for i,t in enumerate(all_cols):
    #     st.write(f'Σ {t}',str(df.iloc[-1,i].round(2)),'m')
    
    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        st.write('Printed P/D Production: ', df.iloc[-1,0].round(2), 'm')
        st.write('Printed YD Production: ', df.iloc[-1,1].round(2), 'm')
        st.write('Printed P/D Yardage Production: ', df.iloc[-1,2].round(2), 'm')
        st.write('Printed YD Yardage Production: ', df.iloc[-1,3].round(2), 'm')
        st.write('Piece Dyed Production: ', df.iloc[-1,4].round(2), 'm')
        st.write('Print FRC: ', df.iloc[-1,7].round(2), 'm')
        st.write('Print RG/RS Production: ', df.iloc[-1,5].round(2), 'm')
        st.write('Total Print Production: ', df.iloc[-1,8].round(2), 'm')
    
    with col2:
        st.write('Bulk YD Production: ', df.iloc[-1,9].round(2), 'm')
        st.write('YD Yardage Production: ', df.iloc[-1,10].round(2), 'm')
        # st.write('Printed YD Yardage Production', df.iloc[-1,3].round(2), 'm')
        # st.write('Piece Dyed Production', df.iloc[-1,4].round(2), 'm')
        st.write('YD FRC: ', df.iloc[-1,13].round(2), 'm')
        st.write('YD RG/RS Production: ', df.iloc[-1,11].round(2), 'm')
        st.write('Total YD Production: ', df.iloc[-1,14].round(2), 'm')

    with col3:
        st.write('All Total Production: ', (df.iloc[-1,8]+df.iloc[-1,14]).round(2), 'm')
        st.write('All Total Production (including PD Production): ', (df.iloc[-1,8]+df.iloc[-1,14]+df.iloc[-1,4]).round(2), 'm')