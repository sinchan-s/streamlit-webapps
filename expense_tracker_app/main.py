import calendar
from datetime import datetime

import streamlit as st
from streamlit_option_menu import option_menu  #pip install streamlit-option-menu
import plotly.graph_objects as go

import database as db


#! settings
incomes = ["Salary", "Dividend", "Invest Return"]
expenses = ['Food', 'Loan', 'CC Bill', 'Others']
currency = "₹"
page_title = "Income & Expense tracker"
page_icon = ":money_with_wings:"
layout = "centered"

#! intro
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

#! dropdown for date
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

#! database interface
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods

#! clean streamlit styling
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden;}
       footer {visibility: hidden;}
       header {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

#! nav menu
selected = option_menu(
    menu_title=None, 
    options=['Transaction entry', 'Visualize expense'],
    icons=['pencil-fill', 'bar-chart-fill'],
    orientation='horizontal')

#! input & save periods
if selected == 'Transaction entry':
    st.header(f'Enter your daily transactions')
    with st.form('entry_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key="month")
        col2.selectbox("Select Year:", years, key="year")
        "---"
        with st.expander("Income"):
            for income in incomes:
                st.number_input(f'{income}:', min_value=0, format="%i", step=10, key=income)
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f'{expense}:', min_value=0, format="%i", step=10, key=expense)
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here....")
        "---"
        submitted = st.form_submit_button("Save Data")
        if submitted:
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for expense in expenses}
            db.insert_period(period, incomes, expenses, comment)
            st.success('Data saved!')

#! plotting
if selected == 'Visualize expense':
    st.header("Period-wise Visualization")
    with st.form("saved_periods"):
        period = st.selectbox("Select Period:", get_all_periods())
        submitted = st.form_submit_button("Plot period")
        if submitted:
            period_data = db.get_period(period)
            comment = period_data.get("comment")
            expenses = period_data.get("expenses")
            incomes = period_data.get("incomes")

            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            savings = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total income", f'{currency} {total_income}')
            col2.metric("Total expense", f'{currency} {total_expense}')
            col3.metric("Savings", f'{currency} {savings}')
            st.text(f'Comment: {comment}')

            #! create sankey chart
            label = list(incomes.keys()) + ['Total income'] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses]
            value = list(incomes.values()) + list(expenses.values())

            #! data to dict & dict to sankey
            link = dict(source=source, target=target, value=value, color = ['#98cc9b','#98cc9b','#98cc9b','#e18685','#e18685','#e18685','#e18685'])
            node = dict(label=label, pad=90, thickness=13, color = ['#2ba02b','#2ba02b','#2ba02b','#2ba02b','#cc0202','#cc0202','#cc0202','#cc0202'])
            data = go.Sankey(link=link, node=node)

            #! plotting
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=15, r=15, t=25, b=25))
            st.plotly_chart(fig, use_container_width=True)