from deta import Deta
import streamlit as st

#! initialize QuickFibre database & drive
def load_deta():
    DETA_KEY = st.secrets["DETA_KEY"]
    deta = Deta(DETA_KEY)
    db = deta.Base("quickfibre_db")
    drive = deta.Drive("quickfibre_drive")
    return db, drive

deta_connect = load_deta()
qf_db = deta_connect[0]
qf_drive = deta_connect[1]


#*------------------------------------------------------------------------------------------*#
#*                                       DETA functions                                     *#
#*------------------------------------------------------------------------------------------*#
#! db: user credentials input
insert_user = lambda username, name, email, password : qf_db.put({"key": username, "name": name, "email":email, "password": password})

#! db: get a user data
user_data = lambda key : qf_db.get(key)

#! db: get all user data
all_users_data = lambda : qf_db.fetch().items

#! db: update user data
update_user = lambda username, updates : qf_db.update(updates, username)

#! db: delete user data
delete_user = lambda username : qf_db.delete(username)

drive_upload = lambda file : qf_drive.put(file.name, data=file)

drive_list = lambda : qf_drive.list()['names']

drive_fetch = lambda fname: qf_drive.get(fname)
