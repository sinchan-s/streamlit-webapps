
#! standard librabries
import re, random
import pandas as pd
import numpy as np
import streamlit as st
import database as db
import datetime

#! addtional libs
from annotated_text import annotated_text, annotation
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
from streamlit_carousel import carousel
from streamlit_extras.stateful_button import button 

#! basic configurations
st.set_page_config(
    page_title="QucikFibre",                   #? similar to <title> tag
    page_icon=":four_leaf_clover:",               #? page icon
    layout="wide",                              #? widen-out view of the layout
    initial_sidebar_state="expanded")          #? side-bar state when page-load

#! clean footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

#! an apt heading
left_col, right_col = st.columns(2, gap='large')
left_col.title(":four_leaf_clover: QuickFibre")
db.load_deta()

#! products highlight & nav menu
test_items = [
    dict(title="Apparels",
        text="Our inhouse garmenting facility",
        interval=None,
        img="https://www.vardhman.com/images/Businesses/Garments/Banner.jpg"),
    dict(title="Yarns",
        text="Prime producer of premium quality yarns",
        img="https://www.vardhman.com/images/Businesses/Yarns/Banner.jpg"),
    dict(title="Fabrics",
        text="Vertically integrated fabric suppliers",
        img="https://www.vardhman.com/images/Businesses/Fabrics/Banner.jpg"),
]


#! UAC - user account control
# https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
#! fetch all users data from database
users = db.all_users_data()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
emails = [user["email"] for user in users]
hashed_passwords = [user["password"] for user in users]

#! consolidating user credentials
check = {}
for uname, name, email, pword in zip(usernames, names, emails, hashed_passwords):
    check[uname] = {"name": name, "email": email, "password": pword}
credentials = {"usernames": check}

#! authentication object
authenticator = stauth.Authenticate(credentials=credentials, key="qfibre_sign",
    cookie_name="qfibre_auth_cookie", cookie_expiry_days=0, preauthorized="check@email.com")

#! display user login
name , auth_status, username = authenticator.login('Account Login', 'sidebar')

#! user-auth: if fails or none
if auth_status==None or auth_status==False:
    #! image carousel to show
    carousel(items=test_items, width=1)
    #! sidebar items: new_user_register, forgot_password
    with st.sidebar:
        st.warning('Enter username & password !')
        col1, col2 = st.columns(2, gap='large')
        with col1: user_register_btn = button("New User Register", key='reg')
        if user_register_btn:
            try:
                register_user = authenticator.register_user('Register user', preauthorization=False)
                if register_user:
                    st.success('User registered successfully')
            except Exception as e:
                st.error(e)
        with col2: forgot_pass = button("Forgot Password", key='forgot_pass')
        if forgot_pass:
            try:
                username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password('Forgot Password')
                if username_of_forgotten_password:
                    st.success('New password to be sent securely')
                else:
                    st.error('Username not found')
            except Exception as e:
                st.error(e)

#! user-auth: if succeeds
elif auth_status==True:
    col1, col2 = st.columns([4, 1])
    #! main heading & detail
    with col1:
        st.header("Welcome to the world of possibilities !!")
        st.caption("Click on menu items to navigate")
    #! vertical navbar
    with col2:
        nav_menu = option_menu(None, ["Home", "Variety", "Enquiry", "Account"], 
            icons=['house-fill', 'flower3', "grid", 'person-fill'], 
            menu_icon="list", default_index=0, orientation="vertical",
            styles={
            "container": {"padding": "0!important", "background-color": "#f0f0f0"},
            "icon": {"color": "#fccc08", "font-size": "15px"}, 
            "nav-link": {"color": "black","font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#bfbfbf"},
            "nav-link-selected": {"background-color": "#008b47"},
        })

#*------------------------------------------------------------------------------------------*#
#*                                      Sidebar Controls                                    *#
#*------------------------------------------------------------------------------------------*#
    #! sidebar user account control
    with st.sidebar:
        #! user details
        st.image('quickfibre/images/ph.jpeg')
        st.image('quickfibre/images/user-f1.png')     
        st.write(f'Welcome, **{name}**(@{username}) !')
        st.caption('-{company}')
        st.caption(f'Email: {credentials["usernames"][username]["email"]}')
        st.caption("Credit Score: {score}")
        #! account buttons - 6 buttons
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            user_search = st.button(':mag:', help='Search') #?button-1
            user_addresses = st.button(':factory:', help='Addresses') #?button-2
        with col2:
            user_account = st.button(':male-office-worker:', help='Account') #?button-3
            user_transact = button(':currency_exchange:', key='transact', help='Transactions') #?button-4
        with col3: user_collect = st.button(':womans_clothes:', help='Collections') #?button-5
        with col4: user_chat = st.button(':speech_balloon:', help='Chat Support') #?button-6
        #! logout button
        authenticator.logout('Logout', 'sidebar')
        st.divider()
        col1, col2 = st.columns(2, gap='large')
        #! password reset button
        with col1: pass_reset = button("Reset Password", key='reset')
        if pass_reset:
            try:
                if authenticator.reset_password(username, form_name='Reset Password'):
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(e)
        #! update details button
        with col2: update_details = button("Update details", key='update_details')
        if update_details:
            try:
                if authenticator.update_user_details(username, 'Update Details'):
                    st.success('Entries updated successfully')
            except Exception as e:
                st.error(e)

#*------------------------------------------------------------------------------------------*#
#*                                      Test dataframe                                      *#
#*------------------------------------------------------------------------------------------*#
    #! reading the source files
    articles_df = pd.read_csv("quickfibre/data/articles.csv",encoding= 'unicode_escape')    
    orders_df = pd.read_csv("quickfibre/data/sitedata2k.csv",encoding= 'unicode_escape')      

    #! column extraction from construction column function to extractor columns 
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

    #! dropdown lists & dicts
    spin_dict = {'All': "", 'Carded':'K', 'Carded Compact': 'K.COM', 'Combed': 'C', 'Combed Compact': 'C.COM', 'Vortex':'VOR', 'Open-End':'OE'}
    count_list = [6, 7, 8, 10, 12, 14, 15, 16, 20, 21, 30, 32, 40, 45, 50, 60, 80, 100]
    fibre_dict = {'All':"", 'Viscose':"VIS", 'Modal':"MOD", 'CVC':"CVC", 'Polyester':"PET", 'PC-Blend':"PC", 'Nylon':"NYL", 'Spandex/Lycra':"SPX", 'Lyocell':"LYC", 'Organic Cotton':"OG", 'Recycled Cotton':"RECY", 'Multi-Count':"MC"}
    weave_list = ["", 'PLAIN', 'TWILL', 'SATIN', 'DOBBY', 'CVT', 'MATT', 'HBT', 'BKT', 'OXFORD', 'DOUBLE CLOTH', 'BEDFORD CORD', 'RIBSTOP', 'WEFTRIB']
    effect_dict = {'Normal': "", 'Seer Sucker': 'SUCKER', 'Crepe': 'CREPE', 'Butta-Cut': 'FIL-COUPE', 'Crinkle': 'CRINKLE', 'Slub':"MC"}

#*------------------------------------------------------------------------------------------*#
#*                                  Account buttons control                                 *#
#*------------------------------------------------------------------------------------------*#
#! Search button control
#! Account button control
#! Collections button control
#! Chat-support button control
#! Address button control
    #! Transaction button control
    if user_transact:
        with st.expander(label="**Transactions**", expanded=True):
            row_count = orders_df.shape[0]
            pay_type = ['NEFT', 'UPI', 'RTGS', 'Unavailable']
            pay_amt = np.random.randint(100000, 1000000, size=row_count)
            pay_status = ['Paid', 'Unpaid', 'Unsuccessful']
            pay_ai_check = ['✓ (verified)', 'X (not verified)', '↻ (in-process)']
            today = datetime.datetime.now()
            next_year = today.year + 1
            feb_28 = datetime.date(today.year, 2, 28)
            mar_17 = datetime.date(today.year, 3, 17)
            st.caption("AI-based order verification system")
            if st.toggle("Search by options"):
                left_col, right_col = st.columns(2, gap='small')
                with left_col:
                    search_by_order = st.selectbox("Order No.", orders_df['Doc No'])
                    search_by_status = st.selectbox("Status", pay_status)
                with right_col:
                    st.date_input("Date", (feb_28, datetime.date(today.year, 3, 7)),feb_28, mar_17, format="DD/MM/YYYY",)
                    search_by_mode = st.selectbox("Mode", pay_type)
            # st.dataframe(orders_df.loc[orders_df['Doc No']==order_select])
            # st.image('quickfibre/images/transaction.jpg')
            transact_dict = {'Order ID': orders_df['Doc No'],
                            'Date': orders_df['Doc Date'],
                            'Mode': random.choices(pay_type, k=row_count),
                            'Status':random.choices(pay_status, k=row_count),
                            'Amount (₹)': random.choices(pay_amt, k=row_count),
                            'Verification': random.choices(pay_ai_check, k=row_count)}
            transact_df = pd.DataFrame(transact_dict)
            # transact_select_df = transact_select_df[transact_select_df['gsm'].between(gsm_range[0], gsm_range[1]) & transact_select_df['epi'].between(epi_range[0], epi_range[1]) & transact_select_df['ppi'].between(ppi_range[0], ppi_range[1])]
            try:
                transact_select_df = transact_df[transact_df['Order ID'].str.contains(search_by_order, na=False) &
                                            transact_df['Mode'].str.contains(search_by_mode, na=False) |
                                            transact_df['Status'].str.contains(search_by_status, na=False)]
            except:
                transact_select_df = transact_df
            st.dataframe(transact_select_df, use_container_width=True)

#*------------------------------------------------------------------------------------------*#
#*                                        Home Menu                                         *#
#*------------------------------------------------------------------------------------------*#
    if nav_menu=="Home":
        #! home page carousel
        col1, col2, col3 = st.columns(3, gap='large')
        col1.image('https://www.vardhman.com/images/Businesses/Garments/Banner.jpg')
        col1.write('Apparels')
        col2.image('https://www.vardhman.com/images/Businesses/Yarns/Banner.jpg')
        col2.write('Yarns')
        col3.image('https://www.vardhman.com/images/Businesses/Fabrics/Banner.jpg')
        col3.write('Fabrics')

#*------------------------------------------------------------------------------------------*#
#*                                      Variety Menu                                        *#
#*------------------------------------------------------------------------------------------*#
    if nav_menu=="Variety":
        #! fabric variety options
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<a href="#"><img src="https://img1.exportersindia.com/product_images/bc-full/dir_102/3054382/yarn-dyed-fabrics-1182473.jpg" height=100 width=150 style="border: 2px solid orange"></a>',unsafe_allow_html=True)
            st.write("Yarn Dyed")
            st.markdown('<a href="#"><img src="https://dineshexports.com/wp-content/uploads/2021/03/FC-R6C-scaled.jpg" height=100 width=150 style="border: 2px solid orange"></a>',unsafe_allow_html=True)
            st.write("RFD / White")
        with col2:
            st.markdown('<a href="#"><img src="https://image.made-in-china.com/202f0j00NMifhGWnywoy/100-Polyester-Microfiber-Dyed-Fabric-for-Hometextile.webp" height=100 width=150 style="border: 2px solid orange"></a>',unsafe_allow_html=True)
            st.write("Piece Dyed")
            st.markdown('<a href="#"><img src="https://www.sustainme.in/cdn/shop/articles/o_1_1400x.jpg" height=100 width=150 style="border: 2px solid orange"></a>',unsafe_allow_html=True)
            st.write("Organic")
        with col3:
            st.markdown('<a href="#"><img src="https://d1jsd7iv7h2l7v.cloudfront.net/wp-content/uploads/2021/08/Sky-Blue-Floral-Print-on-Poly-Twill-Dress-Material-Fabric-16366-2.jpg" height=100 width=150 style="border: 2px solid orange"></a>',unsafe_allow_html=True)
            st.write("Prints")
            st.markdown('<a href="#"><img src="https://genwoo.sg/cdn/shop/articles/recycled-fabric-scaled.webp" height=100 width=150 style="border: 2px solid orange"></a>',unsafe_allow_html=True)
            st.write("Recycled")

#*------------------------------------------------------------------------------------------*#
#*                                      Enquiry Menu                                        *#
#*------------------------------------------------------------------------------------------*#
    if nav_menu=="Enquiry":
        #! fabric selection criteria
        with st.container(height=400):
            st.write("**_Fabric Specs selection_**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Warp Parameters**")
                warp_fibre_select = st.selectbox("Fibre", list(fibre_dict), help="Dropdown list of fibres used in warp")
                warp_count_select = str(st.select_slider("Count", count_list, help="Count selector: Warp"))
                warp_spin_select = st.selectbox("Spinning technology", list(spin_dict),  help="Spinning technology of warp")
                warp_ply_check = st.checkbox(f'Doube ply: {warp_count_select} Ne', key=1, help=f"Check for doube ply in {warp_count_select} Ne")
                if warp_ply_check:
                    warp_value = '2/' + warp_count_select
                else:
                    warp_value = warp_count_select
                warp_regex = '^'+warp_value+spin_dict.get(warp_spin_select)
                same_for_weft = st.checkbox('Same parameters for Weft')
            with col2:
                st.markdown("**Weft Parameters**")
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
            with col3:
                st.markdown("**Construction**")
                epi_range = st.slider('EPI range', 50, 210, (60, 150))
                ppi_range = st.slider('PPI range', 50, 200, (60, 150))
                weave_selectbox = st.selectbox("Weave", weave_list, help="Select the fabric weave")
                effect_selectbox = st.selectbox("Effect", list(effect_dict), help="Select any special effect on fabric")
                gsm_range = st.slider('GSM range', 120, 350, (150, 200))

        selection_df = article_df[article_df['Construction'].str.contains(weave_selectbox) & article_df['Construction'].str.contains(effect_dict.get(effect_selectbox))]

        # selection_df = selection_df[selection_df['gsm'].between(gsm_range[0], gsm_range[1]) & selection_df['epi'].between(epi_range[0], epi_range[1]) & selection_df['ppi'].between(ppi_range[0], ppi_range[1])]
        # selection_df = article_df[article_df['warp'].str.contains('^6[a-zA-Z]*', na=False)]

        #! filtered & all data - dataframe display
        tab1, tab2 = st.tabs(['Filtered Data', 'All Data'])
        with tab1:
            pass
            selection_df = selection_df.set_index('K1')
            df_display = st.dataframe(selection_df, use_container_width=True)
        with tab2:
            df_display = st.dataframe(orders_df, use_container_width=True)


#*------------------------------------------------------------------------------------------*#
#*                                      Account Menu                                        *#
#*------------------------------------------------------------------------------------------*#
    if nav_menu=="Account":
        if button('Your Orders', key='ord'):
            col1, col2 = st.columns([2,1], gap='small')
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
                st.dataframe(orders_df[orders_df['Ord. Qty']>=500].T)
            if order_type=='Yardage':
                st.dataframe(orders_df[orders_df['Ord. Qty'].between(200, 500)].T)
            if order_type=='Deskloom':
                st.dataframe(orders_df[orders_df['Ord. Qty']<=200].T)
            if order_type=='Lab-Dip':
                st.dataframe(orders_df[orders_df['Ord. Qty']<=200].T)
            if order_type=='Strike-off':
                st.dataframe(orders_df[orders_df['Ord. Qty']<=200].T)
        with st.expander("**Order Activities**", expanded=True):
            order_select = st.selectbox("Select order:", orders_df['Doc No'])
            
            left_col, right_col = st.columns(2, gap='large')
            with left_col:
                if button('Availability/Status', key='avail'):
                    ord_avail = st.selectbox("Check for:", ['Order Status', 'Hangers', 'Feasibility', 'Developments', 'Fabric Availability'])
                    if ord_avail=='Order Status':
                        try:
                            st.write(f"Dispatch remaining: {orders_df.loc[orders_df['Doc No']==order_select]['Bal to Dispatch'][0]} m")
                            st.write(f"Expected delivery: {orders_df.loc[orders_df['Doc No']==order_select]['Doc Date'][0].split(' ')[0]}")
                        except:
                            st.write(f"Dispatch remaining: 0 m")
                            st.write(f"Expected delivery: 2024-03-28")
                    else:
                        pass
            with right_col:
                if button('Reports/Certificates', key='activ'):
                    activities = ['Dispatch details', 'Packing List', 'Inspection Report', 'Head Ends deatils', 'External Test Report(FPT)', 'Internal Test report(ITR)', 'Organic Certificates', 'GOTS Certificates', 'BCI Certificates', 'Lenzing Certificates', 'OCS Certificates', 'Lot Details', 'Shade Cards', 'FSC Certificates', 'GI Certificates', 'Compliances', 'Garments Compliances']
                    activity_select = st.selectbox("Select file to download:", activities)
                    st.download_button(label=f"Download", data='quickfibre/dummy.pdf', file_name='dummy.pdf')
