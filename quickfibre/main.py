
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
from streamlit_extras.stateful_button import button 

#! basic configurations
st.set_page_config(
    page_title="QucikFibre",                   #! similar to <title> tag
    page_icon=":womans_clothes:",               #! page icon
    layout="wide",                              #! widen-out view of the layout
    initial_sidebar_state="expanded")          #! side-bar state when page-load

#! clean footer
# hide_default_format = """
#        <style>
#        #MainMenu {visibility: hidden;}
#        footer {visibility: hidden;}
#        </style>
#        """
# st.markdown(hide_default_format, unsafe_allow_html=True)


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
#? db: user credentials input
insert_user = lambda username, name, password : qf_db.put({"key": username, "name": name, "password": password})

#? db: get a user data
user_data = lambda key : qf_db.get(key)

#? db: get all user data
all_users_data = lambda : qf_db.fetch().items

#? db: update user data
update_user = lambda updates, username : qf_db.update(updates, username)

#? db: delete user data
delete_user = lambda username : qf_db.delete(username)

drive_upload = lambda file : qf_drive.put(file.name, data=file)

drive_list = lambda : qf_drive.list()['names']

drive_fetch = lambda fname: qf_drive.get(fname)

#! an apt heading
left_col, right_col = st.columns(2, gap='large')
left_col.header("QuickFibre")
# left_col.caption("Your idea Our creation")


#! products highlight & nav menu
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



#! sidebar contents
st.sidebar.image('quickfibre/images/ph.png')  #? location

#! user account control
# https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
with open('quickfibre/data/config.yaml') as file:   #? location
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

if auth_status==None:
    carousel(items=test_items, width=1)
    with st.sidebar:
        st.warning('Enter correct credentials !!')
        if button("Signup", key='reg'):
            try:
                if authenticator.register_user('Register user', preauthorization=False):
                    st.success('User registered successfully')
            except Exception as e:
                st.error(e)
# elif auth_status==None:
#     st.sidebar.warning('Enter credentials to continue')
#     carousel(items=test_items, width=1)
elif auth_status==True:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("Welcome to the world of possibilities !!")
        st.caption("Click on the side controls to navigate")
    with col2:
        nav_menu = option_menu(None, ["Home", "Variety", "Enquiry", "Account"], 
            icons=['house', 'cloud-upload', "list-task", 'gear'], 
            menu_icon="cast", default_index=0, orientation="vertical",
            styles={
            "container": {"padding": "0!important", "background-color": "#f1f1f1"},
            "icon": {"color": "#fccc08", "font-size": "15px"}, 
            "nav-link": {"color": "black","font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#bfbfbf"},
            "nav-link-selected": {"background-color": "#008b47"},
        })
    col1, col2, col3 = st.columns(3, gap='large')
    if nav_menu=="Home":
        col1.image('https://www.vardhman.com/images/Businesses/Garments/Banner.jpg')
        col1.write('Vardhman Apparels')
        col2.image('https://www.vardhman.com/images/Businesses/Yarns/Banner.jpg')
        col2.write('Vardhman Yarns')
        col3.image('https://www.vardhman.com/images/Businesses/Fabrics/Banner.jpg')
        col3.write('Vardhman Fabrics')

#*------------------------------------------------------------------------------------------*#
#*                                      Sidebar Controls                                    *#
#*------------------------------------------------------------------------------------------*#
    #! Sidebar UAC
    with st.sidebar:
        #! user account details
        st.image('quickfibre/images/user-ph.png')     #? location
        st.write(f'Welcome, **{name}** !')
        st.caption(f'{username}')
        st.caption('{company}')
        st.caption('{email}')
        st.caption("Credit Score: {score}")
        #! account buttons
        col1, col2, col3, col4 = st.columns(4, gap='large')
        col1.button(':mag:', help='Search')
        col2.button(':male-office-worker:', help='Account')
        col3.button(':womans_clothes:', help='Collections')
        col4.button(':speech_balloon:', help='Chat Support')
        authenticator.logout('Logout', 'sidebar')

    #! reading the source files
    articles_df = pd.read_csv("quickfibre/data/articles.csv",encoding= 'unicode_escape')    #? location
    orders_df = pd.read_csv("quickfibre/data/sitedata2k.csv",encoding= 'unicode_escape')      #? location


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

#*------------------------------------------------------------------------------------------*#
#*                                      Variety Section                                     *#
#*------------------------------------------------------------------------------------------*#
    if nav_menu=="Variety":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Yarn Dyed")
            st.button("RFD")
        with col2:
            st.button("Piece Dyed")
            st.button("Organic")
        with col3:
            st.button("Prints")
            st.button("Recycled")


#*------------------------------------------------------------------------------------------*#
#*                                      Enquiry Section                                     *#
#*------------------------------------------------------------------------------------------*#
    if nav_menu=="Enquiry":
        #! selection criteria
        col1, col2, col3 = st.columns(3)
        warp_fibre_select = col1.selectbox("Fibre", list(fibre_dict), help="Dropdown list of fibres used in warp")
        warp_count_select = str(col1.select_slider("Count", count_list, help="Count selector: Warp"))
        warp_spin_select = col1.selectbox("Spinning technology", list(spin_dict),  help="Spinning technology of warp")
        warp_ply_check = col1.checkbox(f'Doube ply: {warp_count_select} Ne', key=1, help=f"Check for doube ply in {warp_count_select} Ne")
        if warp_ply_check:
            warp_value = '2/' + warp_count_select
        else:
            warp_value = warp_count_select
        warp_regex = '^'+warp_value+spin_dict.get(warp_spin_select)
        # st.write(warp_regex)
        same_for_weft = col1.checkbox('Same parameters for Weft')
        weft_fibre_select = col2.selectbox("Fibre", list(fibre_dict), help="Dropdown list of fibres used in weft")
        weft_count_select = str(col2.select_slider("Count", count_list, help="Count selector: Weft"))
        weft_spin_select = col2.selectbox("Spinning technology", list(spin_dict),  help="Spinning technology of weft")
        weft_ply_check = col2.checkbox(f'Doube ply: {weft_count_select} Ne', key=2, help=f"Check for doube ply in {weft_count_select} Ne")
        if same_for_weft:
            weft_regex = warp_regex
        else:
            if weft_ply_check:
                weft_value = '2/' + weft_count_select
            else:
                weft_value = weft_count_select
            weft_regex = '^'+weft_value+spin_dict.get(weft_spin_select)
        # st.write(weft_regex)
        epi_range = col3.slider('EPI range', 50, 210, (60, 150))
        ppi_range = col3.slider('PPI range', 50, 200, (60, 150))
        weave_selectbox = col3.selectbox("Weave", weave_list, help="Select the fabric weave")
        effect_selectbox = col3.selectbox("Effect", list(effect_dict), help="Select any special effect on fabric")
        gsm_range = col3.slider('GSM range', 120, 350, (150, 200))

        selection_df = article_df[article_df['Construction'].str.contains(weave_selectbox) &
                                    article_df['Construction'].str.contains(effect_dict.get(effect_selectbox))]

        # selection_df = selection_df[selection_df['gsm'].between(gsm_range[0], gsm_range[1]) & selection_df['epi'].between(epi_range[0], epi_range[1]) & selection_df['ppi'].between(ppi_range[0], ppi_range[1])]
        # selection_df = article_df[article_df['warp'].str.contains('^6[a-zA-Z]*', na=False)]

        #! dataframe display
        tab1, tab2 = st.tabs(['Filtered Data', 'All Data'])
        with tab1:
            pass
            selection_df = selection_df.set_index('K1')
            df_display = st.dataframe(selection_df)
        with tab2:
            df_display = st.dataframe(orders_df)


#*------------------------------------------------------------------------------------------*#
#*                                      Account Section                                     *#
#*------------------------------------------------------------------------------------------*#
    if nav_menu=="Account":
        if button('Your Orders', key='ord'):
            col1, col2 = st.columns([2,1], gap='small')
            # if button('Status', key='stat'):
            order_type = option_menu(
                menu_title=None, 
                options=['Bulk', 'Yardage', 'Deskloom', 'Lab-Dip', 'Strike-off'], 
                icons=[], 
                orientation='horizontal',
                styles={
                "container": {"padding": "0!important", "background-color": "#f1f1f1"},
                "icon": {"color": "#fccc08", "font-size": "15px"}, 
                "nav-link": {"color": "black","font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#bfbfbf"},
                "nav-link-selected": {"background-color": "#008b47"},
            })
            if order_type=='Bulk':
                st.dataframe(orders_df[orders_df['Ord. Qty']>=500])
            if order_type=='Yardage':
                st.dataframe(orders_df[orders_df['Ord. Qty'].between(200, 500)])
            if order_type=='Deskloom':
                st.dataframe(orders_df[orders_df['Ord. Qty']<=200])
            if order_type=='Lab-Dip':
                st.dataframe(orders_df[orders_df['Ord. Qty']<=200])
            if order_type=='Strike-off':
                st.dataframe(orders_df[orders_df['Ord. Qty']<=200])
            collect_type = option_menu(
                menu_title=None, 
                options=['Hangers', 'Store', 'Availability'], 
                icons=[], 
                orientation='horizontal',
                styles={
                "container": {"padding": "0!important", "background-color": "#f1f1f1"},
                "icon": {"color": "#fccc08", "font-size": "15px"}, 
                "nav-link": {"color": "black","font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#bfbfbf"},
                "nav-link-selected": {"background-color": "#008b47"},
            })
            collect_type
