
#! Important Libraries
import io, os, math, base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image
from fpdf import FPDF
from deta import Deta
from fpdf.fonts import FontFace
from datetime import date, time, datetime
# from streamlit_cropper import st_cropper
from streamlit_option_menu import option_menu  #pip install streamlit-option-menu
from matplotlib.backends.backend_pdf import PdfPages
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

#*------------------------------------------------------------------------------------------*#
#*                                    Unique key generator                                  *#
#*------------------------------------------------------------------------------------------*#
key = str(math.ceil(datetime.now().timestamp()))

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

upload_data = lambda defect_type, customer, article, po_no, qty, remarks : defects_base.put({"key": key, "Date": date, "Defect_type": defect_type, "Customer": customer, "Article": article, "PO": po_no, "Quantity": qty, "Remarks": remarks})

fetch_data = lambda key : defects_base.get(key)

fetch_all_data = lambda : defects_base.fetch().items

convert_df = lambda df : df.to_csv().encode('utf-8')


#*------------------------------------------------------------------------------------------*# 
#*                                      PDF settings init                                   *#
#*------------------------------------------------------------------------------------------*#
pdf = FPDF()
pdf.add_page()
pdf.set_font('helvetica', size=20)

#*------------------------------------------------------------------------------------------*# 
#*                                    NAV-1: Defects Entry                                  *#
#*------------------------------------------------------------------------------------------*#
if selected=='Defects Entry':

    img_file = st.sidebar.file_uploader(label='Upload a file', type=['png', 'jpg'])
    realtime_update = st.sidebar.checkbox(label="Update in Real Time", value=True)
    box_color = st.sidebar.color_picker(label="Box Color", value='#0000FF')
    aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=["1:1", "16:9", "4:3", "2:3", "Free"])
    aspect_dict = {
        "1:1": (1, 1),
        "16:9": (16, 9),
        "4:3": (4, 3),
        "2:3": (2, 3),
        "Free": None
    }
    aspect_ratio = aspect_dict[aspect_choice]

    #!------------image display-upload
    col1, col2, col3 = st.columns(3, gap="large")
    placeholder_img = Image.open('place_h.jpg')
    cam_access = col2.toggle(':camera: Take picture')
    user_img = col1.file_uploader(":frame_with_picture: Upload image", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])
    cam_disabled_state = True
    cam_img = user_img
    if cam_access:
        cam_disabled_state = False
        cam_img = col3.camera_input(":camera:", disabled=cam_disabled_state)

    #!------------details add-on
    defects_list = ['Slubs', 'Splices', 'Lining', 'Patta', 'Dropping', 'SM & TP', 'Leno issue', 'Neps', 'Stain', 'Shade variation']
    col1, col2, col3 = st.columns(3, gap="large")
    date_inp = col1.date_input(':calendar: Select date:', datetime.now())
    time_inp = col1.time_input(':timer_clock: Select time')
    date = date_inp.strftime("%d-%m-%Y")
    defects = col2.multiselect("Defect Type:", defects_list)
    m_defects = col2.text_input("Manually enter Defect type:", placeholder='Enter Defect(s) type')
    customer = col3.text_input("Customer details:", placeholder='End Buyer / Vendor /  Customer')
    k1 = col1.text_input("Article:", placeholder='Finish K1')
    po_no = col3.text_input("PO No:", placeholder='F000000000 / P000000000')
    qty = col2.number_input("Defect quantity observed:")
    remarks = col3.text_area("Additional Remarks:", placeholder='Extra details to add')
    st.divider()

    #!------------data validate conditions
    defect_type = ""
    if not defects:
        defect_type = m_defects                             #? from manual entry
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
        col3.success("Data Uploaded successfully !!")                                  #? upload successful..
        prog_bar.progress(100) #?progress=100%

#*------------------------------------------------------------------------------------------*# 
#*                                NAV-2: Defects History                                    *#
#*------------------------------------------------------------------------------------------*#
if selected=='Defects History':
    col1, col2 = st.columns(2, gap="large")
    #!------------fetch button
    fetch_button = col1.button(label='🔄 Fetch / Refresh Data', use_container_width=True)
    prog_bar = col2.progress(0) #?progress=0%
    if 'defects_data' not in st.session_state:
        st.session_state.defects_data = {'key':0,}
    if fetch_button:
        try:
            with col2:
                st.session_state.defects_data = fetch_all_data()
                prog_bar.progress(100) #?progress=100%
        except:
            err = TimeoutError('Please check your network connection !!')
            st.exception(err)
    try:
        #!------------dataframing the json data
        if 'df' not in st.session_state:
            st.session_state.df = {'key':0,}
        st.session_state.df = pd.DataFrame(st.session_state.defects_data)
        st.session_state.df['Date'] = pd.to_datetime(st.session_state.df.Date, format='%d-%m-%Y')
        st.session_state.df = st.session_state.df[["key", "Date", "Defect_type", "Customer", "Article", "PO", "Quantity", "Remarks"]].set_index('key')
        st.session_state.df = st.session_state.df.sort_values(by='Date',ascending=False)


        #!------------all defects dataframe
        with st.expander('View All Defects Data', expanded=True):
            try:
                transpose_df_view = st.toggle('Transpose View')
                if transpose_df_view:
                    st.data_editor(st.session_state.df.T)
                else:
                    st.dataframe(st.session_state.df)
            except:
                st.error("An error occured while dataframing...	:dizzy_face:")

            #!------------data downloading...
            csv_data = convert_df(st.session_state.df)
            st.download_button(label="📥 Download All Data (.csv)", data=csv_data, file_name='defects_df.csv', mime='text/csv', use_container_width=True)

        #!------------select defect to view
        omni_key = st.selectbox("Search Defect by key:", st.session_state.df.index, on_change=fetch_all_data())

        #!------------defect preview panel
        with st.expander(label='Defect details', expanded=True):
            sel_defect = st.session_state.df[st.session_state.df.index==omni_key]
            col1, col2 = st.columns(2, gap="small")
            with col1:
                img_file = imgs_drive.get(omni_key).read()
                annotated_text(annotation("Image", "", "#28a1e6"),)
                if not img_file:
                    st.error("No Image available !!")
                st.image(img_file, caption=f"{sel_defect.Defect_type[0]} in {sel_defect.Quantity[0]}m of {sel_defect.Customer[0]} fabric")
            with col2:
                annotated_text(annotation("Details", "", "#189c16"),)
                st.table(pd.DataFrame(sel_defect).T)
                more_ops = st.toggle("More options")
                if more_ops:
                    #!------------update data
                    annotated_text(annotation('Update data', "", "#bd660f"),)

                    all_fields = list(st.session_state.df.columns[:])   #?all available fields dropdown
                    all_fields.extend(['Image'])
                    update_key = st.selectbox('Select Field:', all_fields)

                    if update_key=='Quantity':
                        current_val = defects_base.get(omni_key)[update_key]
                        update_value = st.number_input('New Value:', value=current_val)
                    elif update_key=='Image':
                        update_value = st.file_uploader(":frame_with_picture: Upload image", accept_multiple_files=False, type=['png', 'jpeg', 'jpg'])
                    elif update_key=='Date':
                        current_value = st.date_input(":calendar: Select date:", value=datetime.now())
                        update_value = current_value.strftime("%d-%m-%Y")
                    else:
                        current_val = defects_base.get(omni_key)[update_key]
                        update_value = st.text_input(f'New {update_key}:', value=current_val)

                    update_button = st.button(label='Update this data', use_container_width=True, on_click=fetch_all_data())
                    if update_button:
                        prog_bar = st.progress(0) #?progress=0%
                        if update_key=='Image':
                            resize_n_upload_img(image_name=omni_key, image_data=update_value.getvalue())
                        else:
                            defects_base.update({update_key: update_value},omni_key)
                        fetch_all_data()
                        prog_bar.progress(100) #?progress=100%

                    #!------------delete data
                    annotated_text(annotation("Delete", "", "#d11315"),)
                    # st, col2 = st.columns(2, gap="large")
                    del_pass = st.secrets["DEL_PASS"]
                    input_pass = st.text_input('Enter Password to delete data:')
                    del_disabled_status = True
                    if input_pass==del_pass:    #? getting delete access
                        del_disabled_status = False
                    delete_button = st.button(label='Delete this data', disabled=del_disabled_status, use_container_width=True)
                    if delete_button:
                        prog_bar = st.progress(0) #?progress=0%
                        defects_base.delete(omni_key)
                        imgs_drive.delete(omni_key)
                        prog_bar.progress(100) #?progress=100%

        #!------------download section
        # with st.expander(label='Download data (.pdf)', expanded=True):
        #     pdf_df = st.session_state.df[st.session_state.df.index==omni_key]
        #     df_to_list = list([pdf_df.columns.values.tolist()])
        #     df_val_list = pdf_df.values.tolist()
        #     df_to_list.extend(df_val_list)
        #     pdf = FPDF(orientation="landscape")
        #     pdf.add_page()
        #     pdf.set_margin(5)
        #     pdf.set_font("Times", size=12)
        #     white = (255, 255, 255)
        #     black = (0, 0, 0)
        #     headings_style = FontFace(emphasis="BOLD", color=white, fill_color=black)
        #     with pdf.table(line_height=7, text_align="CENTER", headings_style=headings_style) as table:
        #         for data_row in df_to_list:
        #             row = table.row()
        #             for datum in data_row:
        #                 row.cell(str(datum))
        #         re_defect_img = img_file#.resize((400,400))
        #         row = table.row()
        #         row.cell("Defect image", colspan=2)
        #         row.cell(f"{sel_defect.Defect_type[0]} in {sel_defect.Quantity[0]}m of {sel_defect.Customer[0]} fabric", colspan=2)
        #         row.cell(img=re_defect_img, img_fill_width=True, colspan=3)
        #     pdf_data = pdf.output()

        #     # code inspired from: https://discuss.streamlit.io/t/rendering-pdf-on-ui/13505/1
        #     base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        #     pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="600" type="application/pdf">'
        #     st.markdown(pdf_display, unsafe_allow_html=True)
        #     st.download_button(label="Download PDF", data=base64_pdf, mime="application/octet-stream", file_name="Output.pdf")

    except ValueError:
        st.write('Please refresh !!')
