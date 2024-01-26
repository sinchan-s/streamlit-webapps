from deta import Deta
import streamlit as st

#! initialize QuickFibre database & drive
DETA_KEY = st.secrets["DETA_KEY"]
deta = Deta(DETA_KEY)
qf_db = deta.Base("quickfibre_db")
qf_drive = deta.Drive("quickfibre_drive")

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
update_user = lambda username, updates : qf_db.update(updates, username)

#? db: delete user data
delete_user = lambda username : qf_db.delete(username)

drive_upload = lambda file : qf_drive.put(file.name, data=file)

drive_list = lambda : qf_drive.list()['names']

drive_fetch = lambda fname: qf_drive.get(fname)

# insert_user("sinx", "Sinchan", "sinx2024")