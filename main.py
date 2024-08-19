import requests
import sqlite3 
import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt
from tabulate import tabulate
import datetime
import os 

def log_message(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{message}: {current_time}"

def pie_chart():
         unique_values = []
         for row in df.itertuples():
            vector = (row.party_name, row.legal_1)
            unique_values.append(vector)
         unique_values = list(set(unique_values))
         counts = []
         for value in unique_values:
            subset = df[df['legal_1'] == value[1]]
            unique_names = subset['party_name'].unique() 
            subcounts = []
            for name in unique_names:
                subcounts.append(subset['party_name'].value_counts()[name])
            labels = unique_names
            sizes = subcounts
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, colors=plt.cm.Pastel2.colors, autopct='%1.1f%%',
       pctdistance=0.5)
            fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)
            ax.set_title(value[1])
            st.divider() 
            st.pyplot(fig) 
            plt.close()
            counts.append(subset.shape[0])

def format_names(item):
        try:
            name = item.split()
            name = name[1:] + [name[0]]
            name = [x.lower().capitalize() for x in name]
            name = ' '.join(name)
        except IndexError:
            return name[0]
        return name

def make_request(query, max_rows=0, rows_per_page=0, start_row=0):
    headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-length": "61",
    "content-type": "application/json;charset=UTF-8",
    "cookie": "ASP.NET_SessionId=xev1vvrs0gxc4x1scmgweml5",
    "origin": "https://tcweb.glastonbury-ct.gov",
    "priority": "u=1, i",
    "referer": "https://tcweb.glastonbury-ct.gov/publicsearch/",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }

    url = "https://tcweb.glastonbury-ct.gov/publicsearch/api/search"
    data = {
        "Party": query,
        "MaxRows": max_rows,
        "RowsPerPage": rows_per_page,
        "StartRow": start_row
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json() 
    return f"{response.status_code} Error"


st.title("Glastonbury Records") 
query = st.text_input("Search")
if query: 
    data = make_request(query)
    df = pd.DataFrame(data)
    df = df[['rec_date', 'party_name', 'cross_party_name', 'legal_1']]
    df['party_name'] = df['party_name'].apply(format_names)
    
    stat = st.radio('Visual Options', ['transactions', 'pie', 'recency'])
    if stat == 'pie':
         pie_chart() 
    if stat == 'transactions':
         unique_names = df['party_name'].unique()
         for name in unique_names:  
            unique_values = []
            data_points = []
            subset = df[df['party_name'] == name]
            for row in subset.itertuples():
                vector = (row.party_name, row.legal_1, row.rec_date)
                data_point = (row.party_name, row.legal_1)
                unique_values.append(vector)
                data_points.append(data_point)
            unique_values = sorted(unique_values, key = lambda x: x[2])
            t_values = list(set(data_points))
            con = []
            for value in t_values:
                 XY = df[(df['party_name'] == value[0]) & (df['legal_1'] == value[1])]
                 X = df[df["party_name"] == value[0]]
                 supportXY = XY.shape[0] / len(t_values)
                 supportX = X.shape[0] / len(t_values)
                 confidenceXY = supportXY / supportX
                 confidenceXsupport = supportXY * confidenceXY
                 end_vector = (value[0], value[1], confidenceXsupport)
                 con.append(end_vector)
            con = sorted(con, key=lambda x: x[2], reverse=True)
            st.header(name)
            st.code(tabulate(unique_values, tablefmt= 'heavy_outline'))
            st.markdown(f":green[Most Probable Location :] *{con[0][1]}*")

    if stat == 'recency':
         unique_names = df['party_name'].unique()
         for name in unique_names:  
            unique_values = []
            data_points = []
            subset = df[df['party_name'] == name]
            for row in subset.itertuples():
                vector = (row.party_name, row.legal_1, row.rec_date)
                data_point = (row.party_name, row.legal_1)
                unique_values.append(vector)
                data_points.append(data_point)
            unique_values = sorted(unique_values, key = lambda x: x[2], reverse=True)
            threshold = 4
            for value in unique_values:
                try:
                    if not len(value[1].split()) <= threshold or 'RD' in value[1].split() or 'DR' in value[1].split() or 'LA' in value[1].split():
                        address = value[1]
                        break
                    address = 'No Viable Address Found'
                except AttributeError:
                    pass

            st.header(name)
            st.write(f":green[Probable Address :] *{address}*")
    st.divider()
    st.header('Table')
    st.write(log_message("Request made on"))
    st.dataframe(df)
else:
    st.write(f'Search for a last or first name to find the town record.')

         
    


