import math
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
page_title = "Expenz"
page_icon = ":credit_card:"
layout = "centered"

#! intro
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout, menu_items={
        "Get Help": 'mailto:sinchan.tex@outlook.com',
        "Report a bug": "mailto:sinchan.tex@outlook.com",
        "About": '**Daily Expense tracking on the go app**'})
st.title(page_title + " " + page_icon)

#! dropdown for date

#! database interface
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods

#! clean streamlit styling
# hide_default_format = """
#        <style>
#        #MainMenu {visibility: hidden;}
#        footer {visibility: hidden;}
#        header {visibility: hidden;}
#        </style>
#        """
# st.markdown(hide_default_format, unsafe_allow_html=True)

#! nav menu
selected = option_menu(
    menu_title=None, 
    options=['Entry', 'Statistic', 'Transaction'],
    icons=['pencil-fill', 'bar-chart-fill', 'arrow-left-right'],
    orientation='horizontal',
    styles={
            "container": {"padding": "0!important", "background-color": "#f1f1f1"},
            "icon": {"color": "#0502ad", "font-size": "15px"}, 
            "nav-link": {"color": "black","font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#bfbfbf"},
            "nav-link-selected": {"background-color": "#00c284"},
        })

#! Menu-item: Entry
if selected == 'Entry':
    st.subheader(f'Enter your transactions')
    with st.expander("___", expanded=True):
        col1, col2 = st.columns(2)
        calender_date = col1.date_input(label="Date")
        clock_time = col2.time_input(label="Time")
        key = int(datetime.strptime(str(calender_date)+str(clock_time),"%Y-%m-%d%H:%M:%S").timestamp())
        # st.write(key)
        "---"
        transact_type = option_menu(
            menu_title=None, 
            options=['Income', 'Transfer', 'Expense'],
            icons=['arrow-down', 'arrow-repeat', 'arrow-up'],
            orientation='horizontal',
            styles={"container": {"padding": "0!important", "background-color": "#f1f1f1"},
                    "icon": {"color": "#0502ad", "font-size": "15px"}, 
                    "nav-link": {"color": "black","font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#bfbfbf"},
                    "nav-link-selected": {"background-color": "#e6a637"},
                    })
        transact_amount = st.number_input('Amount', min_value=0, format="%i", step=10, key='transact_amt')
        transact_description = st.text_area("Description", placeholder="Short description")
        if transact_type == 'Income' or transact_type == 'Expense':
            transact_category = st.selectbox('Category', ['Investment', 'Salary'])
        if transact_type == 'Transfer':
            primary_account = st.selectbox('From Account', ['Kotak Bank', 'SBI Bank', 'UCO Bank', 'Paytm Bank', 'Cash'])
            secondary_account = st.selectbox('To Account', ['Kotak Bank', 'SBI Bank', 'UCO Bank', 'Paytm Bank', 'Cash'])

        "---"
        submitted = st.button("Save Data")
        if submitted:
            # period = str(calender_date) + "_" + str(tm)
            # st.write(period)
            # incomes = {income: st.session_state[income] for income in incomes}
            # expenses = {expense: st.session_state[expense] for expense in expenses}
            # db.insert_period(period, incomes, expenses, comment)
            st.write(f"{calender_date}\n{clock_time}\n{transact_amount}\n{transact_description}\n{transact_category}")
            st.toast('Data saved!')

#! Menu-item: Statistic
if selected == 'Statistic':
    st.subheader("Period-wise Visualization")
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

#! Menu-item: Transaction
if selected == 'Transaction':
    st.subheader("Transactions history")
    
    #! my wallet db access
    dbfile = 'expense_tracker_app/ignore/wallet-database.db'
    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    table_list = [a[0] for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    with st.expander("Data view expander ", expanded=False):
        selected_table = st.selectbox("Select a table to view inside:", table_list)
        tables_df = st.dataframe(pd.read_sql_query(f'SELECT * FROM {selected_table}', con))
    table_df_list = list()
    for i, table in enumerate(table_list):
        table_df = table + '_df'
        table_df = pd.read_sql_query(f'SELECT * FROM {table_list[i]}', con)
        table_df_list.append(table_df)
    transaction_df = pd.read_sql_query(f'SELECT * FROM {table_list[12]}', con)          #? all transactions table
    df = transaction_df.copy()
    con.close()
    st.write(table_df_list[13])

    st.write(table_df_list[12].merge(table_df_list[13], left_on='wallet_id', right_on='id', suffixes=('_left', '_right')))

    #! data pre-processing
    df['amount'] = df['amount'].div(100).round(2)
    df['trans_amount'] = df['trans_amount'].div(100).round(2)
    df['type'] = df['type'].replace([0, 1, 2], ['inc', 'exp', 'tran'])
    df.drop(['id', 'fee_id', 'account_id', 'debt_id', 'debt_trans_id', 'memo'], axis = 1, inplace = True)
    df['date_time'] = pd.to_datetime(df["date_time"], unit='ms').dt.date
    df = df[['date_time', 'type', 'amount', 'wallet_id', 'category_id', 'transfer_wallet_id', 'trans_amount', 'subcategory_id', 'note']]

    #! categorization of exp-inc
    # category_df.at[0, 'name'] = 'Bills'
    # category_df.at[1, 'name'] = 'Clothing'
    # category_df.at[2, 'name'] = 'Education'
    # category_df.at[5, 'name'] = 'Food'
    # category_df.at[6, 'name'] = 'Gifts'
    # category_df.at[7, 'name'] = 'Medicine'
    # category_df.at[10, 'name'] = 'Shopping'
    # category_df.at[11, 'name'] = 'Transportation'
    # category_df.at[12, 'name'] = 'Travel'
    # category_df.at[13, 'name'] = 'Others'
    # category_df.at[14, 'name'] = 'Adjustments'
    # category_df.at[21, 'name'] = 'Investment returns'
    # category_df.at[23, 'name'] = 'Salary'
    # category_df.at[25, 'name'] = 'Received: Others'
    # category_df.at[26, 'name'] = 'Adjustment'
    # category_df.at[32, 'name'] = 'Received: Cash'

    #! replace wallet-id with wallet-name & category-id with category-name
    df['wallet_id'] = df['wallet_id'].replace(list(set(wallet_df['id'])), list(wallet_df['name']))
    df['transfer_wallet_id'] = df['transfer_wallet_id'].replace(list(set(wallet_df['id'])), list(wallet_df['name'].str.upper()))
    df['category_id'] = df['category_id'].replace(list(set(category_df['id'])), list(category_df['name']))
    df['subcategory_id'] = df['subcategory_id'].replace(list(set(subcategory_df['id'])), list(subcategory_df['name']))
    transfer_df = df[df['category_id'] == 0]
    # expenses_df = df[df['amount'] == 1]
    df = df[df['category_id'] != 0]
    # st.dataframe(expenses_df)

    #! selectors
    # from_date_selector = st.date_input('From date:', datetime.date(2020, 1, 1))
    # to_date_selector = st.date_input('To date:', datetime.date.today())
    wallet_selector = st.multiselect('Select Wallet', sorted(list(set(df['wallet_id']))))
    selected_df = df.loc[(df['wallet_id'].isin(wallet_selector))]
    category_selector = st.multiselect('Select Category', list(set(selected_df['category_id'])))
    selected_df = df.loc[(df['category_id'].isin(category_selector))]
    # subcategory_selector = st.selectbox('Select SubCategory', list(subcategory_df['name']))
    with st.expander('Wallet data', expanded=False):
        st.dataframe(selected_df)
        st.metric('Total', f'₹ {selected_df.amount.sum():,}')

    #?----SankeyChart wrapper function from https://medium.com/kenlok/how-to-create-sankey-diagrams-from-dataframes-in-python-e221c1b4d6b0

    def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
        # maximum of 6 value cols -> 6 colors
        colorPalette = ['#7FD000','#8c5f23','#FFE873','#FFD43B','#646464']
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
    
    fig = genSankey(selected_df, cat_cols=['category_id','wallet_id'], value_cols='amount',title='Money flow')
    st.plotly_chart(fig, use_container_width=True)
    fig2 = genSankey(transfer_df, cat_cols=['wallet_id','transfer_wallet_id'], value_cols='amount',title='Transfer flow')
    st.plotly_chart(fig2, use_container_width=True)
    fig3 = genSankey(df, cat_cols=['category_id','wallet_id'], value_cols='amount',title='Income flow')
    st.plotly_chart(fig3, use_container_width=True)

# with st.expander("Category"):
#     col1, col2, col3, col4, col5 = st.columns(5)
#     col1.button(":chart:", help="Investment")
#     col2.button(":bus:", help="Transportation")
#     col3.button(":shirt:", help="Clothes")
#     col4.button(":iphone:", help="Recharge")
#     col5.button(":gift:", help="Gift")
#     col1.button(":shopping_trolley:", help="Shopping")
#     col2.button(":closed_book:", help="Book")
#     col3.button(":carrot:", help="Carrot")
#     col4.button(":train:", help="Transportation")
#     col5.button(":medical_symbol:", help="Medicals")
