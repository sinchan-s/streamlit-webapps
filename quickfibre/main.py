#! standard librabries
import pandas as pd
import numpy as np
import streamlit as st
import re, pickle, os
from pathlib import Path

#! addtional libs
import yaml
from deta import Deta
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader 
from streamlit_option_menu import option_menu
from streamlit_carousel import carousel

#! basic configurations
st.set_page_config(
    page_title="Qucik Fibre",                   #! similar to <title> tag
    page_icon=":womans_clothes:",               #! page icon
    layout="wide",                              #! widen-out view of the layout
    initial_sidebar_state="expanded")          #! side-bar state when page-load

#! clean footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)


#! initialize deta Base & Drive
def load_data():
    DETA_KEY = st.secrets["DETA_KEY"]
    deta = Deta(DETA_KEY)
    db = deta.Base("quickfibre_db")
    drive = deta.Drive("quickfibre_drive")
    return db, drive

conn = load_data()
qf_db = conn[0]
qf_drive = conn[1]

#*------------------------------------------------------------------------------------------*#
#*                                       DETA functions                                     *#
#*------------------------------------------------------------------------------------------*#
insert_user = lambda username, name, password : qf_db.put({"key": username, "name": name, "password": password})

user_data = lambda key : qf_db.get(key)

all_users_data = lambda : qf_db.fetch().items

update_user = lambda updates, username : qf_db.update(updates, username)

delete_user = lambda username : qf_db.delete(username)

drive_upload = lambda file : qf_drive.put(file.name, data=file)

drive_list = lambda : qf_drive.list()['names']

drive_fetch = lambda fname: qf_drive.get(fname)

#! an apt heading
left_col, right_col = st.columns(2, gap='large')
left_col.header("Quick Fibre")
# left_col.caption("Your idea Our creation")

#! products carousel
test_items = [
    dict(
        title="Vardhman Apparels",
        text="Our inhouse garmenting facility",
        interval=None,
        img="https://www.vardhman.com/images/Businesses/Garments/Banner.jpg",
    ),
    dict(
        title="Vardhman Yarns",
        text="Prime producer of premium quality yarns",
        img="https://www.vardhman.com/images/Businesses/Yarns/Banner.jpg",
    ),
    dict(
        title="Vardhman Fabrics",
        text="Vertically integrated fabric suppliers",
        img="https://www.vardhman.com/images/Businesses/Fabrics/Banner.jpg",
    ),
]

carousel(items=test_items, width=1)

#! sidebar contents
st.sidebar.image('quickfibre/ph.png')

#! user account control
# https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
with open('quickfibre/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
hashed_pass = stauth.Hasher(['abc1234', 'def1234']).generate()
# st.write(hashed_pass)
authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=0,
    preauthorized=config['preauthorized']
)
name , auth_status, username = authenticator.login('Login', 'sidebar')

if auth_status==False:
    st.sidebar.error('Username/Password is incorrect!!')
elif auth_status==None:
    st.sidebar.warning('Enter credentials to continue')
elif auth_status==True:
    #! account details
    with st.sidebar:
        st.image('quickfibre/user-ph.png')
        st.write(f'Welcome, **{name}** !')
        st.caption(f'{username}')
        st.caption('{company}')
        st.caption('{email}')
        st.caption("Credit Score: {score}")
        #! account buttons
        col1, col2, col3, col4 = st.columns(4, gap='large')
        col1.button(':mag:', help='Search')
        col2.button(':male-office-worker:', help='Account')
        col3.button(':womans_clothes:', help='Colections')
        col4.button(':speech_balloon:', help='Chat')
        authenticator.logout('Logout', 'sidebar')

    #! reading the source files
    articles_df = pd.read_csv("quickfibre/articles.csv",encoding= 'unicode_escape')
    orders_df = pd.read_csv("quickfibre/sitedata.csv",encoding= 'unicode_escape')


    #! column extraction from construction column
    #! function to extractor columns 
    def col_ext(df_file):
        columns_list = list(map(str.lower, df_file.columns))
        if 'Construction' in columns_list:
            ext_index = columns_list.index('Construction')
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
            warp_ply_check = st.checkbox(f'Doube ply: {warp_count_select} Ne', key=1, help=f"Check for doube ply in {warp_count_select} Ne")
            if warp_ply_check:
                warp_value = '2/' + warp_count_select
            else:
                warp_value = warp_count_select
            warp_regex = '^'+warp_value+spin_dict.get(warp_spin_select)
            # st.write(warp_regex)
        same_for_weft = st.checkbox('Same parameters for Weft')
    with col2:
        with st.expander('Select Weft Parameters'):
            weft_fibre_select = st.selectbox("Fibre", list(fibre_dict), help="Dropdown list of fibres used in weft")
            weft_count_select = str(st.select_slider("Count", count_list, help="Count selector: Weft"))
            weft_spin_select = st.selectbox("Spinning technology", list(spin_dict),  help="Spinning technology of weft")
            weft_ply_check = st.checkbox(f'Doube ply: {weft_count_select} Ne', key=2, help=f"Check for doube ply in {weft_count_select} Ne")
            if same_for_weft:
                weft_regex = warp_regex
            else:
                if weft_ply_check:
                    weft_value = '2/' + weft_count_select
                else:
                    weft_value = weft_count_select
                weft_regex = '^'+weft_value+spin_dict.get(weft_spin_select)
            # st.write(weft_regex)
    with col3:
        with st.expander('Select Fabric Construction'):
            epi_range = st.slider('EPI range', 50, 210, (60, 150))
            ppi_range = st.slider('PPI range', 50, 200, (60, 150))
            weave_selectbox = st.selectbox("Weave", weave_list, help="Select the fabric weave")
            effect_selectbox = st.selectbox("Effect", list(effect_dict), help="Select any special effect on fabric")
            gsm_range = st.slider('GSM range', 120, 350, (150, 200))

    selection_df = article_df[article_df['Construction'].str.contains(weave_selectbox) &
                                article_df['Construction'].str.contains(effect_dict.get(effect_selectbox))]

    # selection_df = selection_df[selection_df['gsm'].between(gsm_range[0], gsm_range[1]) & selection_df['epi'].between(epi_range[0], epi_range[1]) & selection_df['ppi'].between(ppi_range[0], ppi_range[1])]
    # selection_df = article_df[article_df['warp'].str.contains('^6[a-zA-Z]*', na=False)]
    #*-------------------------------------------------------------------------------------------------------------------------*#

    #! dataframe display
    tab1, tab2 = st.tabs(['Filtered Data', 'All Data'])
    with tab1:
        pass
        selection_df = selection_df.set_index('K1')
        df_display = st.dataframe(selection_df)
    with tab2:
        df_display = st.dataframe(articles_df)

    st.divider()

    #! user account
    col1, col2, col3, col4, col5 = st.columns(5, gap='large')
    col1, col2, col3, col4, col5 = st.columns(5, gap='large')
    col1.button('Orders')
    col2.button('Status')
    st.divider()
    order_type = option_menu(
        menu_title=None, 
        options=['Bulk', 'Yardage', 'Deskloom', 'Lab-dip', 'Stike-off'], 
        icons=[], 
        orientation='horizontal')
    order_type
    st.divider()
    collect_type = option_menu(
        menu_title=None, 
        options=['Hangers', 'Store', 'Availability'], 
        icons=[], 
        orientation='horizontal')
    collect_type
    st.divider()
