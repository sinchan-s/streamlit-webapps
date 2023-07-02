import calendar
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
    layout="centered",
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

#! initialize deta db
DETA_KEY = st.secrets["DETA_KEY"]
deta = Deta(DETA_KEY)
db = deta.Base("defects_db")

#! set title and subtitle
st.title('Daily Defects observation app')

#! image display-upload area
try:
    placeholder_img = Image.open('place_h.jpg')
    col1, col2, col3 = st.columns(3)
    cam_button = col1.button(label='Use System Camera')
    if cam_button:  
        cam_img = col1.camera_input("Take defect image")
        st.image(cam_img)
    user_imgs = col2.file_uploader("Choose photos to upload", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])
    up_imgs = Image.open(user_imgs)
    with col3.expander('image preview'):
        if cam_img is None:
            st.image(up_imgs)
        elif up_imgs is None:
            st.image(cam_img.getvalue())
        else:
            st.image(placeholder_img, caption='Placeholder image')

    st.set_option('deprecation.showfileUploaderEncoding', False)    #? Enabling the automatic file decoder
    submit_button = st.button(label='Upload Images')         #? Submit button
    pic_names = []                                           #? Later used for deleting the local files after being uploaded
    for uploaded_file in user_imgs:                          #? Iterating over each file uploaded
        file = uploaded_file.read()                          #? Read the data
        image_result = open(uploaded_file.name, 'wb')        #? creates a writable image and later we can write the decoded result
        image_result.write(file)                             #? Saves the file with the name uploaded_file.name to the root path('./')
        pic_names.append(uploaded_file.name)                 #? Append the name of image to the list
        image_result.close()                                 #? Close the file pointer
    if submit_button:
        for i in range(len(pic_names)):                      #? Iterating over each file name
            name = pic_names[i]                              #? Getting the name of current file
            path ='./'+pic_names[i]                          #? Creating path string which is basically ["./image.jpg"]
            drive.put(name, path=path)                       #? so, we have our file name and path, so uploading images to the drive
            os.remove(pic_names[i])                          #? Finally deleting it from root folder
        st.success('Uploaded!')                              #? Success message
except:
    print("An exception occurred")

#! details add-on
col1, col2, col3 = st.columns(3)
defects = col1.multiselect("Defect Type", ['Slubs', 'Splices', 'Warp lining'])
customer = col2.text_input("Customer details")
po_no = col2.text_input("Input PO No.")
k1 = col3.text_input("Input Article")
qty = col1.number_input("Defect quantity observed")

#! db functions
def upload_data(image_data, defect_type, details):
    date_time = datetime.now()
    date = date_time.strftime("%m/%d/%Y")
    time = date_time.strftime("%H:%M:%S")
    return db.put({"key": str(date_time.timestamp()), "date": date, "time": time, "image_data": image_data, "defect_type": defect_type, "details": details})

def fetch_data(period):
    return db.get(period)

def fetch_all_data():
    res = db.fetch()
    return res.items

#! upload button function
upload_button = st.button(label='Upload Data')                          #? Upload button
if upload_button:
    image_data = 'type-1'
    defect_type = []
    for i in range(len(defects)):
        defect_type.append(defects[i])
    details = {'Customer': customer, 'PO': po_no, 'K1': k1, 'Qty': qty}
    upload_data(image_data, defect_type, details)
    st.success("Data Uploaded successfully !!")

fetch_button = st.button(label='Fetch Data')
if fetch_button:
    defects_data = fetch_all_data()
    st.success("Data fetched !!")
    df = pd.DataFrame(defects_data)
    df = df[['date', 'time', 'defect_type', 'details']]
    # st.success("Dataframed !!")
    #! downloading...
    def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    csv = convert_df(df)
    st.download_button(
        label="Download data as CSV",
        data=csv, file_name='defects_df.csv',
        mime='text/csv',) 
    #! data display
    "Data display"
    st.json(defects_data)
    st.dataframe(df)
    st.success("Data displayed !!")

    # for i in range(df.shape[0]):
    #     st.image(df.loc[i, 'image_data'])