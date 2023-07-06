import calendar, base64, json, time
from datetime import datetime
from PIL import Image
from deta import Deta
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu  #pip install streamlit-option-menu

#! page configuration
st.set_page_config(
    page_title="Daily defects observation • web-app",
    page_icon=":stop_sign:",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
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
key = str(datetime.now().timestamp())

#! initialize deta Base & Drive
DETA_KEY = st.secrets["DETA_KEY"]
deta = Deta(DETA_KEY)
defects_db = deta.Base("defects_db")
imgs_drive = deta.Drive("defects_imgs")

#! defects_db functions
def upload_data(defect_type, details):
    date_time = datetime.now()
    date = date_time.strftime("%m/%d/%Y")
    time = date_time.strftime("%H:%M:%S")
    return defects_db.put({"key": key, "date": date, "time": time, 
                    "defect_type": defect_type, 
                    "details": details})

def upload_img(image_name, image_data):
    return imgs_drive.put(image_name, data=image_data)

def fetch_data(period):
    return defects_db.get(period)

def fetch_all_data():
    res = defects_db.fetch()
    return res.items

#! set title and subtitle
st.title('Daily Defects observation app')

#! image display-upload
placeholder_img = Image.open('place_h.jpg')
col1, col2, col3 = st.columns(3) 
cam_img = col1.camera_input("Take defect image")
user_imgs = col2.file_uploader("Choose defect image to upload", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])

#! image preview panel
# Some code from: https://stackoverflow.com/questions/74423171/streamlit-image-file-upload-to-deta-drive
with col3.expander('image preview'):
    if cam_img is None and user_imgs is None:
        st.image(placeholder_img, caption='Placeholder image')
        image_data = placeholder_img.getvalue()
    elif user_imgs is None:
        st.image(cam_img, caption=key)
        image_data = cam_img.getvalue()
    else:
        st.image(user_imgs, caption=key)
        image_data = user_imgs.getvalue()

#! details add-on
defects_list = ['Slubs', 'Splices', 'Warp lining']
col1, col2, col3 = st.columns(3)
defects = col1.multiselect("Defect Type", defects_list)
m_defects = col1.text_input("Manually enter defect type:")
customer = col2.text_input("Customer details")
po_no = col2.text_input("Input PO No.")
k1 = col3.text_input("Input Article")
qty = col3.number_input("Defect quantity observed")

#! data validate conditions
if not defects:
    defects = m_defects


#! upload button
upload_button = st.button(label='Upload Data')                          #? Upload button
image_name = key
if upload_button:
    defect_type = ""
    if defects:
        for i in range(len(defects)):
            defect_type = defects[i] + ", "
    details = {'Customer': customer, 'PO': po_no, 'K1': k1, 'Qty': qty}
    prog_bar = st.progress(0)
    upload_data(defect_type, details)
    upload_img(image_name, image_data)
    st.success("Data Uploaded successfully !!")
    prog_bar.progress(100)

#! fetch button
fetch_button = st.button(label='Fetch All Data')
if fetch_button:
    prog_bar = st.progress(0)
    defects_data = fetch_all_data()
    prog_bar.progress(100)
    df = pd.DataFrame(defects_data)
    
    st.success("Data fetched !!")
        
    img_key = st.selectbox("All Defect images:", df.key)
    # defect_select = st.selectbox('Select defect:', df.defect_type)
    # img_key = df[df.defect_type.str.contains(defect_select)].key[0]
    # st.write('img_key:  '+ img_key)

    try:
        st.image(Image.open(imgs_drive.get(img_key)))
    except:
        st.error("Image can't be displayed")
    df = df[['date', 'time', 'defect_type', 'details', 'image_name']]

    #! data downloading...
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(df)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='defects_df.csv',
        mime='text/csv',)

    #! data display
    with st.expander('Raw Data Preview:'):
        st.json(defects_data)
    try:
        st.table(df)
    except:
        st.error("An error occured while dataframing...🙁")