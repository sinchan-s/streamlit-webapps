
#! important librabries
import pandas as pd
import numpy as np
import streamlit as st
import re

#! basic configurations
st.set_page_config(
    page_title="Qucik Fibre",                   #! similar to <title> tag
    page_icon=":womans_clothes:",               #! page icon
    layout="wide",                              #! widen-out view of the layout
    initial_sidebar_state="collapsed")          #! side-bar state when page-load

#! clean Footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

#! reading the source files
articles_df = pd.read_csv("sitedata.csv",encoding= 'unicode_escape')

#! an apt heading
st.header("Quick Fibre")
st.subheader("Your idea Our creation")

#! column extraction from construction column
#! function to extractor columns 
def col_ext(df_file):
    all_columns = list(map(str.lower, df_file.columns))
    if 'Finish Construction' in all_columns:
        ext_index = all_columns.index('Finish Construction')
        df_file['warp'] = df_file.iloc[:, ext_index].str.extract(r'^([\d\w\s+.\/()]*)[*]')
        df_file['weft'] = df_file.iloc[:, ext_index].str.extract(r'^[\d\w\s+.\/()]*[*]([\d\w\s+.\/()]+)')
        df_file['epi'] = df_file.iloc[:, ext_index].str.extract(r'[-](\d{2,3})[*]').astype('float64')
        df_file['ppi'] = df_file.iloc[:, ext_index].str.extract(r'[*](\d{2,3})[-]').astype('float64')
        df_file['width'] = df_file.iloc[:, ext_index].str.extract(r'[-*](\d{3}\.?\d{0,2})-').astype('float64')
        df_file['weave'] = df_file.iloc[:, ext_index].str.extract(r'-(\d?\/?\d?[,\s]?[A-Z]+\s?[A-Z]*\(?[A-Z\s]+\)?)')
        df_file['gsm'] = df_file.iloc[:, ext_index].str.extract(r'[-\s](\d{3}\.?\d?)[\s$]*$').astype('float64')
    return df_file

article_df = col_ext(articles_df)
# st.dataframe(article_df)

#! dropdown lists & dicts
spin_dict = {'All': "", 'Carded':'K', 'Carded Compact': 'K.COM', 'Combed': 'C', 'Combed Compact': 'C.COM', 'Vortex':'VOR', 'Open-End':'OE'}
count_list = [6, 7, 8, 10, 12, 14, 15, 16, 20, 21, 30, 32, 40, 45, 50, 60, 80, 100]
fibre_dict = {'All':"", 'Viscose':"VIS", 'Modal':"MOD", 'CVC':"CVC", 'Polyester':"PET", 'PC-Blend':"PC", 'Nylon':"NYL", 'Spandex/Lycra':"SPX", 'Lyocell':"LYC", 'Organic Cotton':"OG", 'Recycled Cotton':"RECY", 'Multi-Count':"MC"}
weave_list = ["", 'PLAIN', 'TWILL', 'SATIN', 'DOBBY', 'CVT', 'MATT', 'HBT', 'BKT', 'OXFORD', 'DOUBLE CLOTH', 'BEDFORD CORD', 'RIBSTOP', 'WEFTRIB']
effect_dict = {'Normal': "", 'Seer Sucker': 'SUCKER', 'Crepe': 'CREPE', 'Butta-Cut': 'FIL-COUPE', 'Crinkle': 'CRINKLE', 'Slub':"MC"}

#*-------------------------------------------------------------------------------------------------------------------------*#
#! selection criteria
col1, col2, col3 = st.columns(3)
with col1:
    with st.expander('Select Warp Parameters'):
        warp_fibre_select = st.selectbox("Fibre", list(fibre_dict), help="Dropdown list of fibres used in warp")
        warp_count_select = str(st.select_slider("Count", count_list, help="Count selector: Warp"))
        warp_spin_select = st.selectbox("Spinning technology", list(spin_dict),  help="Spinning technology of warp")
        warp_ply_check = st.checkbox(f'2/{warp_count_select}', key=1, help=f"Check for doube ply in {warp_count_select} count")
        if warp_ply_check:
            warp_value = '2/' + warp_count_select
        else:
            warp_value = warp_count_select
        warp_regex = '^'+warp_value+spin_dict.get(warp_spin_select)
        st.write(warp_regex)
    same_for_weft = st.checkbox('Same parameters for Weft')
with col2:
    with st.expander('Select Weft Parameters'):
        weft_fibre_select = st.selectbox("Fibre", list(fibre_dict), help="Dropdown list of fibres used in weft")
        weft_count_select = str(st.select_slider("Count", count_list, help="Count selector: Weft"))
        weft_spin_select = st.selectbox("Spinning technology", list(spin_dict),  help="Spinning technology of weft")
        weft_ply_check = st.checkbox(f'2/{weft_count_select}', key=2, help=f"Check for doube ply in {weft_count_select} count")
        if same_for_weft:
            weft_regex = warp_regex
        else:
            if weft_ply_check:
                weft_value = '2/' + weft_count_select
            else:
                weft_value = weft_count_select
            weft_regex = '^'+weft_value+spin_dict.get(weft_spin_select)
        st.write(weft_regex)
with col3:
    with st.expander('Select Fabric Construction'):
        epi_range = st.slider('EPI range', 50, 210, (60, 150))
        ppi_range = st.slider('PPI range', 50, 200, (60, 150))
        weave_selectbox = st.selectbox("Weave", weave_list, help="Select the fabric weave")
        effect_selectbox = st.selectbox("Effect", list(effect_dict), help="Select any special effect on fabric")
        gsm_range = st.slider('GSM range', 120, 350, (150, 200))

selection_df = article_df[article_df['construction'].str.contains(weave_selectbox) &
                             article_df['construction'].str.contains(effect_dict.get(effect_selectbox)) & 
                             article_df['warp'].str.contains(warp_regex) &
                             article_df['warp'].str.contains(fibre_dict.get(warp_fibre_select)) & 
                             article_df['weft'].str.contains(weft_regex) & 
                             article_df['weft'].str.contains(fibre_dict.get(weft_fibre_select))]

selection_df = selection_df[selection_df['gsm'].between(gsm_range[0], gsm_range[1]) & selection_df['epi'].between(epi_range[0], epi_range[1]) & selection_df['ppi'].between(ppi_range[0], ppi_range[1])]
# selection_df = article_df[article_df['warp'].str.contains('^6[a-zA-Z]*', na=False)]
#*-------------------------------------------------------------------------------------------------------------------------*#

#! dataframe display
tab1, tab2 = st.tabs(['Filtered Data', 'All Data'])
with tab1:
    selection_df = selection_df.set_index('k1')
    df_display = st.dataframe(selection_df)
with tab2:
    df_display = st.dataframe(articles_df)