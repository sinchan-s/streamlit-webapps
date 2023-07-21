import calendar, base64, json, time, io
from datetime import datetime
from PIL import Image
from deta import Deta
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu  #pip install streamlit-option-menu
# from annotated_text import annotated_text   #pip install st-annotated-text

#!------------page configuration
st.set_page_config(
    page_title="Daily defects observation • web-app",
    page_icon=":memo:",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

#!------------clean streamlit styling
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       header {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

#!------------unique key generator
key = str(datetime.now().timestamp())

#!------------set title and subtitle
st.title('Daily Defects observation app')

#!------------nav menu
selected = option_menu(
    menu_title=None, 
    options=['Defects Entry', 'Defects History'],
    icons=['card-list', 'clipboard2-data'],
    orientation='horizontal')

#!------------initialize deta Base & Drive
# @st.cache_resource(ttl=3600)
def load_data():
    DETA_KEY = st.secrets["DETA_KEY"]
    deta = Deta(DETA_KEY)
    db = deta.Base("defects_db")
    drive = deta.Drive("defects_imgs")
    return db, drive

conn = load_data()
defects_db = conn[0]
imgs_drive = conn[1]

#*------------------------------------------------------------------------------------------*#
#*                                       DETA functions                                     *#
#*------------------------------------------------------------------------------------------*#
#!------------defects_db functions
# @st.cache_data(ttl=3600, show_spinner="uploading...")
def upload_data(defect_type, customer, article, po_no, qty, remarks):
    return defects_db.put({"key": key, "Date": date, "Defect_type": defect_type, "Customer": customer, "Article": article, "PO": po_no, "Quantity": qty, "Remarks": remarks})

# @st.cache_data(ttl=3600)
def resize_n_upload_img(image_name, image_data):
    input_img = Image.open(io.BytesIO(image_data))
    #!--------image resizing
    basewidth = 400     #? confining image width
    wpercent = (basewidth/float(input_img.size[0]))   #? determining the height ratio
    hsize = int((float(input_img.size[1])*float(wpercent)))
    resized_img = input_img.resize((basewidth,hsize), Image.ANTIALIAS)   #? resize image and save
    #!--------pil-image to byte array conversion
    img_byte_arr = io.BytesIO()
    resized_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return imgs_drive.put(image_name, data=img_byte_arr)

# @st.cache_data(ttl=3600)
def fetch_data(key):
    return defects_db.get(key)

# @st.cache_data(ttl=3600, show_spinner="fetching...")
def fetch_all_data():
    res = defects_db.fetch()
    return res.items

def convert_df(df):
    return df.to_csv().encode('utf-8')

#*------------------------------------------------------------------------------------------*# 
#*                                           NAV-1                                          *#
#*------------------------------------------------------------------------------------------*#
if selected=='Defects Entry':

    #!------------image display-upload
    col1, col2, col3 = st.columns(3, gap="large")
    placeholder_img = Image.open('place_h.jpg')
    cam_img = col1.camera_input(":camera: Take photo")
    user_img = col2.file_uploader(":frame_with_picture: Upload image", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])


    #!------------details add-on
    defects_list = ['Slubs', 'Splices', 'Lining', 'Patta', 'Dropping', 'SM & TP', 'Leno issue', 'Neps', 'Oil Stain']
    col1, col2, col3 = st.columns(3, gap="large")
    date_time = col1.date_input(':calendar: Select date:', datetime.now())
    date = date_time.strftime("%d-%m-%Y")
    defects = col1.multiselect("Defect Type:", defects_list)
    m_defects = col1.text_input("Manually enter Defect type:", placeholder='Enter Defect(s) type')
    customer = col2.text_input("Customer details:", placeholder='End Buyer / Vendor /  Customer')
    po_no = col2.text_input("PO No:", placeholder='F000000000 / P000000000')
    k1 = col3.text_input("Article:", placeholder='Finish K1')
    qty = col3.number_input("Defect quantity observed:")
    remarks = col3.text_area("Additional Remarks:", placeholder='Extra details to add')
    st.divider()

    #!------------data validate conditions
    defect_type = ""
    if not defects:
        defect_type = m_defects
    else:
        defect_type = ', '.join(str(d) for d in defects)
    
    #!------------upload preview expander
    # code inspired rom: https://stackoverflow.com/questions/74423171/streamlit-image-file-upload-to-deta-drive
    with st.expander('Preview Upload'):
        col1, col2 = st.columns(2)
        #!------------image section
        if cam_img is None and user_img is None:
            col1.image(placeholder_img, caption='Placeholder image', width=350, use_column_width='auto')
            image_data = placeholder_img
        elif user_img is None:
            col1.image(cam_img, caption=key, width=350)
            image_data = cam_img.getvalue()
        else:
            col1.image(user_img, caption=key, width=350)
            test_img = Image.open(user_img)
            # col1.write(test_img.size)
            image_data = user_img.getvalue()
        #!------------details filled-in
        upload_df = {
            'Defect Type': defect_type,
            'Customer': customer,
            'Quantity': qty,
            'Article': k1,
            'PO': po_no,
            'Remarks': remarks,
        }
        # col2.json(upload_df)
        col2.table(pd.DataFrame(upload_df, index=[key]).T)


    #!------------upload button
    col1, col2, col3 = st.columns(3, gap="large")
    upload_button = col1.button(label='Upload Data ⬆️', use_container_width=True)                          #? Upload button
    if upload_button:
        prog_bar = col2.progress(0) #?progress=0%
        col2.caption('Please wait...')
        resize_n_upload_img(image_name=key, image_data=image_data)                     #? button for image data upload
        upload_data(defect_type=defect_type, customer=customer, article=k1, po_no=po_no, qty=qty, remarks=remarks)                            #? button for text data upload
        col3.success("Data Uploaded successfully !!")                         #? upload successful..
        prog_bar.progress(100) #?progress=100%

#*------------------------------------------------------------------------------------------*# 
#*                                           NAV-2                                          *#
#*------------------------------------------------------------------------------------------*#
if selected=='Defects History':
    col1, col2, col3 = st.columns(3, gap="large")
    #!------------fetch button
    fetch_button = col1.button(label='Fetch / Refresh Data  🔄', use_container_width=True)
    if 'defects_data' not in st.session_state:
        st.session_state.defects_data = {'key':0, }
    if fetch_button:
        with col2:
            prog_bar = st.progress(0) #?progress=0%
            st.session_state.defects_data = fetch_all_data()
            prog_bar.progress(100) #?progress=100%
    try:
        #!------------dataframing the json data
        df = pd.DataFrame(st.session_state.defects_data)
        df = df[["key", "Date", "Defect_type", "Customer", "Article", "PO", "Quantity", "Remarks"]].set_index('key')
        df = df.sort_values(by='key',ascending=False)

        #!------------data downloading...
        csv = convert_df(df)
        col3.download_button(label="Download Data (.csv)  📥", data=csv, file_name='defects_df.csv', mime='text/csv', use_container_width=True)
        
        #!------------all defects dataframe
        with st.expander('View All Defects Data', expanded=True):
            # st.json(st.session_state.defects_data)
            try:
                st.session_state.transpose_df_view = st.checkbox('Transpose View')
                if st.session_state.transpose_df_view:
                    st.data_editor(df.T)
                else:
                    st.dataframe(df)
            except:
                st.error("An error occured while dataframing...	:dizzy_face:")
        
        #!------------select defect to view
        omni_key = st.selectbox("Search Defect by key:", df.index)

        #!------------defect details preview
        with st.expander(label='Defect details', expanded=False):
            sel_defect = df[df.index==omni_key]
            col1, col2 = st.columns(2, gap="small")
            defect_img = Image.open(imgs_drive.get(omni_key))
            if not defect_img:
                col1.error("No Image available !!")
            col1.image(defect_img, caption=f"{sel_defect.Defect_type[0]} in {sel_defect.Quantity[0]}m of {sel_defect.Customer[0]} fabric", width=350)
            col2.table(pd.DataFrame(sel_defect).T)

        #!------------update entry
        with st.expander('Update data'):
            st.metric('Selected entry:', omni_key)
            col1, col2 = st.columns(2, gap="large")

            all_fields = list(df.columns[1:])   #?all available fields dropdown
            all_fields.append('Image')
            update_key = col1.selectbox('Select Field:', all_fields)

            if update_key=='Quantity':
                current_val = defects_db.get(omni_key)[update_key]
                update_value = col1.number_input('New Value:', value=current_val)
            elif update_key=='Image':
                update_value = col1.file_uploader(":frame_with_picture: Upload image", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])
            else:
                current_val = defects_db.get(omni_key)[update_key]
                update_value = col1.text_input('New Value:', value=current_val)
                
            update_button = col2.button(label='Update this entry', use_container_width=True)
            if update_button:
                prog_bar = st.progress(0) #?progress=0%
                if update_key=='Image':
                    resize_n_upload_img(image_name=omni_key, image_data=update_value.getvalue())
                else:
                    defects_db.update({update_key: update_value},omni_key)
                fetch_all_data()
                prog_bar.progress(100) #?progress=100%

        #!------------delete entry
        with st.expander('Delete data'):
            st.metric('Selected entry:', omni_key)
            col1, col2 = st.columns(2, gap="large")
            del_pass = st.secrets["DEL_PASS"]
            input_pass = col1.text_input('Enter Password to delete entry:')
            del_status = True
            if input_pass==del_pass:    #? getting delete access
                del_status = False
            delete_button = col1.button(label='Delete this entry', disabled=del_status, use_container_width=True)
            if delete_button:
                prog_bar = st.progress(0) #?progress=0%
                defects_db.delete(omni_key)
                imgs_drive.delete(omni_key)
                prog_bar.progress(100) #?progress=100%

    except ValueError:
        st.write('Please refresh !!')
    # except:
    #     st.write('Some error occured..🙁')
