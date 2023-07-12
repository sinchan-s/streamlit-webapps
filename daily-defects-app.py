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

#! set title and subtitle
st.title('Daily Defects observation app')

#! nav menu
selected = option_menu(
    menu_title=None, 
    options=['Defects Entry', 'Defects History'],
    icons=['card-list', 'clipboard2-data'],
    orientation='horizontal')

#! initialize deta Base & Drive
DETA_KEY = st.secrets["DETA_KEY"]
deta = Deta(DETA_KEY)
defects_db = deta.Base("defects_db")
imgs_drive = deta.Drive("defects_imgs")

#*------------------------------------------------------------------------------------------*# DETA functions
#! defects_db functions
def upload_data(defect_type, details, remarks):
    time = date_time.strftime("%H:%M:%S")
    return defects_db.put({"key": key, "date": date, "time": time, 
                    "defect_type": defect_type, "details": details, "remarks": remarks})

def upload_img(image_name, image_data):
    return imgs_drive.put(image_name, data=image_data)

def fetch_data(key):
    return defects_db.get(key)

def fetch_all_data():
    res = defects_db.fetch()
    return res.items

def convert_df(df):
    return df.to_csv().encode('utf-8')

#*------------------------------------------------------------------------------------------*# NAV-1
if selected=='Defects Entry':

    #! image display-upload
    col1, col2, col3 = st.columns(3, gap="large")
    placeholder_img = Image.open('place_h.jpg')
    cam_img = col1.camera_input("Take defect image 📷")
    user_img = col2.file_uploader("Choose defect image to upload 📂", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])

    #! image preview panel
    # Some code from: https://stackoverflow.com/questions/74423171/streamlit-image-file-upload-to-deta-drive
    with col3.expander('Image Preview'):
        if cam_img is None and user_img is None:
            st.image(placeholder_img, caption='Placeholder image', width=350, use_column_width='auto')
            image_data = placeholder_img
        elif user_img is None:
            st.image(cam_img, caption=key, width=350)
            image_data = cam_img.getvalue()
        else:
            st.image(user_img, caption=key, width=350)
            image_data = user_img.getvalue()

    #! details add-on
    defects_list = ['Slubs', 'Splices', 'Lining', 'Patta', 'Dropping', 'SM & TP', 'Leno issue', 'Neps']
    col1, col2, col3 = st.columns(3, gap="large")
    date_time = col1.date_input('Select date 📅:', datetime.now())
    date = date_time.strftime("%d-%m-%Y")
    defects = col1.multiselect("Defect Type:", defects_list)
    m_defects = col1.text_input("Manually enter Defect type:")
    customer = col2.text_input("Customer details:")
    po_no = col2.text_input("PO No:")
    k1 = col3.text_input("Article:")
    qty = col3.number_input("Defect quantity observed:")
    remarks = col3.text_area("Additional Remarks:")
    st.divider()

    #! data validate conditions
    if defects:
        for i in range(len(defects)):
            defect_type = defects[i] + ", "
    else:
        defect_type = m_defects

    #! upload button
    col1, col2, col3 = st.columns(3, gap="large")
    upload_button = col1.button(label='Upload Data ⬆️', use_container_width=True)                          #? Upload button
    if upload_button:
        details = {'Customer': customer, 'PO': po_no, 'K1': k1, 'Qty': qty}
        prog_bar = col2.progress(0) #?progress=0%
        upload_img(image_name=key, image_data=image_data)                     #? button for image data upload
        upload_data(defect_type, details, remarks)                            #? button for text data upload
        col3.success("Data Uploaded successfully !!")                         #? upload successful..
        prog_bar.progress(100) #?progress=100%

#*------------------------------------------------------------------------------------------*# NAV-2
if selected=='Defects History':
    col1, col2 = st.columns(2, gap="large")
    #! fetch button
    fetch_button = col1.button(label='Fetch / Refresh Data  🔄', use_container_width=True)
    if 'defects_data' not in st.session_state:
        st.session_state.defects_data = {'key':0, }
    if fetch_button:
        with col2:
            prog_bar = st.progress(0) #?progress=0%
            st.session_state.defects_data = fetch_all_data()
            prog_bar.progress(100) #?progress=100%
    try:
        #! dataframing the json data
        df = pd.DataFrame(st.session_state.defects_data)
        df = df[['key', 'date', 'defect_type', 'details', 'remarks']].set_index('key')
            
        omni_key = col1.selectbox("Select Defect(key):", df.index)

        #! data downloading...
        csv = convert_df(df)
        col2.download_button(label="Download Data (.csv)  📥", data=csv, file_name='defects_df.csv', mime='text/csv', use_container_width=True)
        
        sel_defect = df[df.index==omni_key]
        # st.write(sel_defect.details[0]['Qty'])

        #! selected defect details preview
        with st.expander(label='Defect details', expanded=True):
            col1, col2 = st.columns(2, gap="large")
            defect_img = Image.open(imgs_drive.get(omni_key))
            if not defect_img:
                col1.error("No Image available !!")
            col1.image(defect_img, caption=f"{sel_defect.defect_type[0]} in {sel_defect.details[0]['Qty']}m of {sel_defect.details[0]['Customer']} fabric", width=300, use_column_width='always')
            disp_df = {
                'Defect Type': sel_defect.defect_type,
                'Customer': sel_defect.details[0]['Customer'],
                'Quantity': sel_defect.details[0]['Qty'],
                'Article': sel_defect.details[0]['K1'],
                'PO': sel_defect.details[0]['PO'],
                'Remarks': sel_defect.remarks,
            }
            col2.table(pd.DataFrame(disp_df).T)

        #! all defects data expander
        st.divider()
        with st.expander('All Defects Data'):
            # st.json(st.session_state.defects_data)
            try:
                st.session_state.transpose_df_view = st.checkbox('Transpose View')
                if st.session_state.transpose_df_view:
                    st.dataframe(df.T)
                else:
                    st.dataframe(df)
            except:
                st.error("An error occured while dataframing...🙁")

        #! delete entry
        st.divider()
        col1, col2 = st.columns(2, gap="large")
        delete_key = col1.selectbox("Select entry to delete:", df.index)
        delete_button = col2.button(label='Delete this entry', disabled=True, use_container_width=True)
        if delete_button:
            prog_bar = st.progress(0) #?progress=0%
            defects_db.delete(omni_key)
            imgs_drive.delete(omni_key)
            prog_bar.progress(100) #?progress=100%
    except ValueError:
        st.write('Please refresh !!')
    # except:
    #     st.write('Some error occured..🙁')
