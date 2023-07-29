import calendar, base64, json, time, io, os
from datetime import datetime
from PIL import Image
from deta import Deta
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu  #pip install streamlit-option-menu
from annotated_text import annotated_text, annotation   #pip install st-annotated-text

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
defects_base = conn[0]
imgs_drive = conn[1]

#*------------------------------------------------------------------------------------------*#
#*                                       DETA functions                                     *#
#*------------------------------------------------------------------------------------------*#
#!------------defects_base functions
# @st.cache_data(ttl=3600, show_spinner="uploading...")
def upload_data(defect_type, customer, article, po_no, qty, remarks):
    return defects_base.put({"key": key, "Date": date, "Defect_type": defect_type, "Customer": customer, "Article": article, "PO": po_no, "Quantity": qty, "Remarks": remarks})

# @st.cache_data(ttl=3600)
def resize_n_upload_img(image_name, image_data):
    img_size = len(image_data)/1024     #?image size
    input_img = Image.open(io.BytesIO(image_data))
    #!--------image resizing
    if img_size >= 1024:
        basewidth = 400     #? confining image width
        wpercent = (basewidth/float(input_img.size[0]))   #? determining the height ratio
        hsize = int((float(input_img.size[1])*float(wpercent)))
        input_img = input_img.resize((basewidth,hsize), Image.ANTIALIAS)   #? resize image and save
    #!--------pil-image to byte array conversion
    img_byte_arr = io.BytesIO()
    input_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    #!--------putting the image data with its name
    return imgs_drive.put(image_name, data=img_byte_arr)

# @st.cache_data(ttl=3600)
def fetch_data(key):
    return defects_base.get(key)

# @st.cache_data(ttl=3600, show_spinner="fetching...")
def fetch_all_data():
    res = defects_base.fetch()
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
    cam_access = col2.checkbox('Camera Access')
    user_img = col1.file_uploader(":frame_with_picture: Upload image", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])
    cam_disabled_state = True
    if cam_access:
        cam_disabled_state = False
    cam_img = col3.camera_input(":camera:", disabled=cam_disabled_state)

    #!------------details add-on
    defects_list = ['Slubs', 'Splices', 'Lining', 'Patta', 'Dropping', 'SM & TP', 'Leno issue', 'Neps', 'Stain', 'Shade variation']
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
        defect_type = m_defects #? from manual entry
    else:
        defect_type = ', '.join(str(d) for d in defects)    #? from dropdown list
    
    #!------------upload preview expander
    # code inspired from: https://stackoverflow.com/questions/74423171/streamlit-image-file-upload-to-deta-drive
    with st.expander('Preview Upload'):
        col1, col2 = st.columns(2)
        #!------------image section
        with col1:
            if cam_img is None and user_img is None:
                st.image(placeholder_img, caption='Placeholder image', width=350, use_column_width='auto')
                image_data = placeholder_img
            elif cam_img is None:
                st.image(user_img, caption=key, width=350)
                test_img = Image.open(user_img)
                image_data = user_img.getvalue()
            else:
                st.image(cam_img, caption=key, width=350)
                image_data = cam_img.getvalue()
        #!------------details filled-in
        with col2:
            upload_df = {
                'Defect Type': defect_type,
                'Customer': customer,
                'Quantity': qty,
                'Article': k1,
                'PO': po_no,
                'Remarks': remarks,
            }
            st.table(pd.DataFrame(upload_df, index=[key]).T)

    #!------------upload button
    col1, col2, col3 = st.columns(3, gap="large")
    upload_button = col1.button(label='⬆️ Upload Data*', use_container_width=True)                          #? Upload button
    col1.caption("*Please don't press Upload button multiple times, it will create duplicate entries")
    prog_bar = col2.progress(0) #?progress=0%
    if upload_button:
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
    fetch_button = col1.button(label='🔄 Fetch / Refresh Data', use_container_width=True)
    prog_bar = col2.progress(0) #?progress=0%
    if 'defects_data' not in st.session_state:
        st.session_state.defects_data = {'key':0,}
    if fetch_button:
        with col2:
            st.session_state.defects_data = fetch_all_data()
            prog_bar.progress(100) #?progress=100%
    try:
        #!------------dataframing the json data
        if 'df' not in st.session_state:
            st.session_state.df = {'key':0,}
        st.session_state.df = pd.DataFrame(st.session_state.defects_data)
        st.session_state.df = st.session_state.df[["key", "Date", "Defect_type", "Customer", "Article", "PO", "Quantity", "Remarks"]].set_index('key')
        st.session_state.df = st.session_state.df.sort_values(by='key',ascending=False)

        #!------------data downloading...
        csv = convert_df(st.session_state.df)
        col3.download_button(label="📥 Download Data (.csv)", data=csv, file_name='defects_df.csv', mime='text/csv', use_container_width=True)
        
        #!------------all defects dataframe
        with st.expander('View All Defects Data', expanded=True):
            # st.json(defects_data)
            try:
                transpose_df_view = st.checkbox('Transpose View')
                if transpose_df_view:
                    st.data_editor(st.session_state.df.T)
                else:
                    st.dataframe(st.session_state.df)
            except:
                st.error("An error occured while dataframing...	:dizzy_face:")
        
        #!------------select defect to view
        omni_key = st.selectbox("Search Defect by key:", st.session_state.df.index, on_change=fetch_all_data)

        #!------------defect preview panel
        with st.expander(label='Defect details', expanded=True):
            sel_defect = st.session_state.df[st.session_state.df.index==omni_key]
            col1, col2 = st.columns(2, gap="small")
            defect_img = Image.open(imgs_drive.get(omni_key))
            if not defect_img:
                col1.error("No Image available !!")
            col1.image(defect_img, caption=f"{sel_defect.Defect_type[0]} in {sel_defect.Quantity[0]}m of {sel_defect.Customer[0]} fabric")
            col2.table(pd.DataFrame(sel_defect).T)


        #!------------update entry
        with st.expander('Update data'):
            annotated_text(annotation(omni_key, "Selected entry", font_family="Source Sans Pro", border="2px dashed cyan"),)
            col1, col2 = st.columns(2, gap="large")

            all_fields = list(st.session_state.df.columns[1:])   #?all available fields dropdown
            all_fields.append('Image')
            update_key = col1.selectbox('Select Field:', all_fields)

            if update_key=='Quantity':
                current_val = defects_base.get(omni_key)[update_key]
                update_value = col1.number_input('New Value:', value=current_val)
            elif update_key=='Image':
                update_value = col1.file_uploader(":frame_with_picture: Upload image", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])
            else:
                current_val = defects_base.get(omni_key)[update_key]
                update_value = col1.text_input('New Value:', value=current_val)
                
            update_button = col2.button(label='Update this entry', use_container_width=True, on_click=fetch_all_data)
            prog_bar = st.progress(0) #?progress=0%
            if update_button:
                if update_key=='Image':
                    resize_n_upload_img(image_name=omni_key, image_data=update_value.getvalue())
                else:
                    defects_base.update({update_key: update_value},omni_key)
                fetch_all_data()
                prog_bar.progress(100) #?progress=100%

        #!------------delete entry
        with st.expander('Delete data'):
            annotated_text(annotation(omni_key, "Selected entry", font_family="Source Sans Pro", border="2px dashed red"),)
            col1, col2 = st.columns(2, gap="large")
            del_pass = st.secrets["DEL_PASS"]
            input_pass = col1.text_input('Enter Password to delete entry:')
            del_disabled_status = True
            if input_pass==del_pass:    #? getting delete access
                del_disabled_status = False
            delete_button = col1.button(label='Delete this entry', disabled=del_disabled_status, use_container_width=True)
            prog_bar = st.progress(0) #?progress=0%
            if delete_button:
                defects_base.delete(omni_key)
                imgs_drive.delete(omni_key)
                prog_bar.progress(100) #?progress=100%

    except ValueError:
        st.write('Please refresh !!')
