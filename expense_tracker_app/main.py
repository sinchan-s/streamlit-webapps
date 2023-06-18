import calendar
import sqlite3
import datetime
from datetime import datetime

import pandas as pd
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
    options=['Transaction entry', 'Visualize expense', 'My Wallet Viewer'],
    icons=['pencil-fill', 'bar-chart-fill', 'wallet2'],
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

#! my wallet
if selected == 'My Wallet Viewer':
    st.header("Date-wise Visualization")
    
    #! my wallet db access
    dbfile = 'ignore/wallet-database.db'
    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    transaction_df = pd.read_sql_query('SELECT * FROM trans', con)          #? all transactions table
    df = transaction_df.copy()
    walletId_df = pd.read_sql_query('SELECT * FROM wallet', con)            #? all wallet ids table
    category_df = pd.read_sql_query('SELECT * FROM category', con)          #? all category ids table
    subcategory_df = pd.read_sql_query('SELECT * FROM subcategory', con)    #? all subcategory ids table
    con.close()

    #! data pre-processing
    df['amount'] = df['amount'].div(100).round(2)
    df['trans_amount'] = df['trans_amount'].div(100).round(2)
    df['type'] = df['type'].replace([0, 1, 2], ['inc', 'exp', 'tran'])
    df.drop(['id', 'fee_id', 'account_id', 'debt_id', 'debt_trans_id', 'memo'], axis = 1, inplace = True)
    df['date_time'] = pd.to_datetime(df["date_time"], unit='ms').dt.date
    df = df[['date_time', 'type', 'amount', 'wallet_id', 'category_id', 'transfer_wallet_id', 'trans_amount', 'subcategory_id', 'note']]

    #! categorization of exp-inc
    category_df.at[32, 'name'] = 'Cash received'
    category_df.at[0, 'name'] = 'Bills'
    category_df.at[1, 'name'] = 'Clothing'
    category_df.at[2, 'name'] = 'Education'
    category_df.at[5, 'name'] = 'Food'
    category_df.at[6, 'name'] = 'Gifts'
    category_df.at[7, 'name'] = 'Medicine'
    category_df.at[10, 'name'] = 'Shopping'
    category_df.at[11, 'name'] = 'Transportation'
    category_df.at[12, 'name'] = 'Travel'
    category_df.at[13, 'name'] = 'Others'
    category_df.at[14, 'name'] = 'Adjustments'
    category_df.at[21, 'name'] = 'Investment returns'
    category_df.at[23, 'name'] = 'Salary'
    category_df.at[25, 'name'] = 'Others received'
    category_df.at[26, 'name'] = 'Adjustment'
    
    #! replace wallet-id with wallet-name & category-id with category-name
    df['wallet_id'] = df['wallet_id'].replace(list(walletId_df['id'].unique()), list(walletId_df['name']))
    df['category_id'] = df['category_id'].replace(list(category_df['id'].unique()), list(category_df['name']))
    df['subcategory_id'] = df['subcategory_id'].replace(list(subcategory_df['id'].unique()), list(subcategory_df['name']))
    
    #! selectors
    # from_date_selector = st.date_input('From date:', datetime.date(2020, 1, 1))
    # to_date_selector = st.date_input('To date:', datetime.date.today())
    wallet_selector = st.selectbox('Select Wallet', list(df['wallet_id']))
    selected_df = df.loc[(df['wallet_id']==wallet_selector)]
    category_selector = st.selectbox('Select Category', list(selected_df['category_id'].unique()))
    selected_df = df.loc[(df['category_id']==category_selector)]
    # subcategory_selector = st.selectbox('Select SubCategory', list(subcategory_df['name']))
    with st.expander('Wallet data', expanded=False):
        st.dataframe(selected_df)

    #?----SankeyChart wrapper function from https://medium.com/kenlok/how-to-create-sankey-diagrams-from-dataframes-in-python-e221c1b4d6b0

    def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
        # maximum of 6 value cols -> 6 colors
        colorPalette = ['#7FD000','#FF2861','#FFE873','#FFD43B','#646464']
        labelList = []
        colorNumList = []
        for catCol in cat_cols:
            labelListTemp =  list(set(df[catCol].values))
            colorNumList.append(len(labelListTemp))
            labelList = labelList + labelListTemp
            
        # remove duplicates from labelList
        labelList = list(dict.fromkeys(labelList))
        
        # define colors based on number of levels
        colorList = []
        for idx, colorNum in enumerate(colorNumList):
            colorList = colorList + [colorPalette[idx]]*colorNum
            
        # transform df into a source-target pair
        for i in range(len(cat_cols)-1):
            if i==0:
                sourceTargetDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
                sourceTargetDf.columns = ['source','target','count']
            else:
                tempDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
                tempDf.columns = ['source','target','count']
                sourceTargetDf = pd.concat([sourceTargetDf,tempDf])
            sourceTargetDf = sourceTargetDf.groupby(['source','target']).agg({'count':'sum'}).reset_index()
            
        # add index for source-target pair
        sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
        sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))
        
        # creating the sankey diagram
        data = dict(
            type='sankey',
            node = dict(
            pad = 15,
            thickness = 20,
            line = dict(
                color = "black",
                width = 0.5
            ),
            label = labelList,
            color = colorList
            ),
            link = dict(
            source = sourceTargetDf['sourceID'],
            target = sourceTargetDf['targetID'],
            value = sourceTargetDf['count']
            )
        )
        
        layout =  dict(
            title = title,
            font = dict(
            size = 10
            )
        )
        
        fig = dict(data=[data], layout=layout)
        return fig
    
    fig = genSankey(df, cat_cols=['wallet_id','category_id'], value_cols='amount',title='My Expenses flow')
    st.plotly_chart(fig, use_container_width=True)
    # with st.form("saved_periods"):
    #     period = st.selectbox("Select Period:", get_all_periods())
    #     submitted = st.form_submit_button("Plot period")
    #     if submitted:
    #         period_data = db.get_period(period)
    #         comment = period_data.get("comment")
    #         expenses = period_data.get("expenses")
    #         incomes = period_data.get("incomes")

    #         total_income = sum(incomes.values())
    #         total_expense = sum(expenses.values())
    #         savings = total_income - total_expense
    #         col1, col2, col3 = st.columns(3)
    #         col1.metric("Total income", f'{currency} {total_income}')
    #         col2.metric("Total expense", f'{currency} {total_expense}')
    #         col3.metric("Savings", f'{currency} {savings}')
