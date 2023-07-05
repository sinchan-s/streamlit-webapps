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
db = deta.Base("defects_db")
img_drive = deta.Drive("defects_imgs")

#! set title and subtitle
st.title('Daily Defects observation app')

#! image display-upload
try:
    placeholder_img = Image.open('place_h.jpg')
    col1, col2, col3 = st.columns(3) 
    cam_img = col1.camera_input("Take defect image")
    user_imgs = col2.file_uploader("Choose photos to upload", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])

    with col3.expander('image preview'):
        if cam_img is None:
            st.image(user_imgs, caption=key)
            image_data = user_imgs.getvalue()
        elif user_imgs is None:
            st.image(cam_img, caption=key)
            image_data = cam_img.getvalue()
        else:
            st.image(placeholder_img, caption='Placeholder image')
except:
    print("An exception occurred")

# Below code from: https://stackoverflow.com/questions/74423171/streamlit-image-file-upload-to-deta-drive

    # st.set_option('deprecation.showfileUploaderEncoding', False)    #? Enabling the automatic file decoder
    # submit_button = st.button(label='Upload Images')                #? Submit button
    # pic_names = []                                                  #? Later used for deleting the local files after being uploaded
    # for uploaded_file in user_imgs:                                 #? Iterating over each file uploaded
    #     file = uploaded_file.read()                                 #? Read the data
    #     image_result = open(uploaded_file.name, 'wb')               #? creates a writable image and later we can write the decoded result
    #     image_result.write(file)                                    #? Saves the file with the name uploaded_file.name to the root path('./')
    #     pic_names.append(uploaded_file.name)                        #? Append the name of image to the list
    #     image_result.close()                                        #? Close the file pointer
    # if submit_button:
    #     for i in range(len(pic_names)):                             #? Iterating over each file name
    #         name = pic_names[i]                                     #? Getting the name of current file
    #         path ='./'+pic_names[i]                                 #? Creating path string which is basically ["./image.jpg"]
    #         drive.put(name, path=path)                              #? so, we have our file name and path, so uploading images to the drive
    #         os.remove(pic_names[i])                                 #? Finally deleting it from root folder
    #     st.success('Uploaded!')                                     #? Success message

#! details add-on
defects_list = ['Slubs', 'Splices', 'Warp lining']
col1, col2, col3 = st.columns(3)
defects = col1.multiselect("Defect Type", defects_list)
m_defects = col1.text_input("Manually enter defect type:")
if defects is None:
    defects = m_defects
customer = col2.text_input("Customer details")
po_no = col2.text_input("Input PO No.")
k1 = col3.text_input("Input Article")
qty = col3.number_input("Defect quantity observed")

#! db functions
def upload_data(image_name, defect_type, details):
    date_time = datetime.now()
    date = date_time.strftime("%m/%d/%Y")
    time = date_time.strftime("%H:%M:%S")
    return db.put({"key": key, "date": date, "time": time, "image_name": key, "defect_type": defect_type, "details": details})

def upload_img(image_name, image_data):
    # path = './'+ image_name
    return img_drive.put(image_name, data=image_data)

def fetch_data(period):
    return db.get(period)

def fetch_all_data():
    res = db.fetch()
    return res.items

#! upload button
upload_button = st.button(label='Upload Data')                          #? Upload button
image_name = key
if upload_button:
    if image_data is None:
        st.error("No image uploaded")
    defect_type = ""
    for i in range(len(defects)):
        defect_type = defects[i] + ", "
    details = {'Customer': customer, 'PO': po_no, 'K1': k1, 'Qty': qty}
    prog_bar = st.progress(0)
    upload_data(image_name, defect_type, details)
    upload_img(image_name, image_data)
    st.success("Data Uploaded successfully !!")
    prog_bar.progress(100)

#! fetch button
fetch_button = st.button(label='Fetch All Data')
if fetch_button:
    prog_bar = st.progress(0)
    defects_data = fetch_all_data()
    # img_select = st.selectbox("All Defects:", img_files)
    prog_bar.progress(100)
    st.success("Data fetched !!")
    df = pd.DataFrame(defects_data)
    defect_select = st.selectbox('Select previous defect:', df.defect_type)
    img_key = df[df.defect_type.str.contains(defect_select)].key[0]
    # st.write(img_key)
    st.image(img_drive.get(img_key).read(), width=450)
    df = df[['date', 'time', 'defect_type', 'details', 'image_name']]

    #! downloading...
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
        st.dataframe(df)
    except:
        st.error("An error occured while dataframing...🙁")