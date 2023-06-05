import os
from deta import Deta
from dotenv import load_dotenv

load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

#! initialize with project key
deta = Deta(DETA_KEY)

#! create/connect a database
db = deta.Base("exp_tracker_app")

def insert_period(period, incomes, expenses, comment):
    """Returns monthly report"""
    return db.put({"key": period, "incomes": incomes, "expenses": expenses, "comment": comment})

def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items

def get_period(period):
    return db.get(period)