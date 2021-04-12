import streamlit as st
import pandas as pd
import requests
import json
import time
import folium
from streamlit_folium import folium_static

def user_input_features():
    #df = pd.read_excel("refined_input.xlsx")
    df = pd.read_excel("refined_input.xlsx")
    
    Service_List=['Chiropractic','Dental','Massage Therapy','Physiotherapy','Vision']
    service_select = st.sidebar.selectbox('Healthcare service',Service_List, 0)

    df_city = df[df["Service"]==service_select]
    city_list = df_city["City"].unique()
    Cities = st.sidebar.selectbox('City', sorted(city_list),0)

    filter_list = ['','10 places with the highest rating','Rating between 4.5~5.0','Rating between 4.0~4.4']
    filter_select = st.sidebar.selectbox('Rating filter',filter_list,0)

    key_word = st.sidebar.text_input("Please type keyword")

    data = [service_select, Cities, filter_select, key_word]
    return data

#take service type & city as input 
#return the address & name of the place from the excel file
def get_place_info():
    data = user_input_features()

    service = data[0]
    city = data[1]
    filter = data[2]
    key_word = data[3]

    df_2 = pd.read_excel("refined_input.xlsx")
    df_word = pd.read_excel("word_list2.xlsx")

    #retrieve the addr & name of the organization 
    #that match the above two requirements
    df_req = df_2[(df_2["Service"]==service) & (df_2["City"]==city)]
    df_req = df_req.reset_index(drop=True)

    #apply rating filter conditions
    if(filter == '10 places with the highest rating'):
        df_req = df_req.nlargest(10, 'Rating')
    
    if(filter == 'Rating between 4.5~5.0'):
        df_req = df_req[(df_req["Rating"]>=4.5) & (df_req["Rating"]<=5)]
    
    if(filter == 'Rating between 4.0~4.4'):
        df_req = df_req[(df_req["Rating"]>=4.0) & (df_req["Rating"]<=4.4)]

    #apply search word conditions
    if(len(key_word)>0):
        w = df_word[df_word["Word"] == key_word]
        w = w.reset_index(drop=True)
        df_final = df_req
        num_row = len(w.index)
        for i in range(0,num_row):
            sc  = w["Address"][i]
            if(sc in df_req["Address"].values):
                df_final = df_req[df_req["Address"]==sc]
                if(len(df_final.index)<=0 or len(df_req.index)<=0):
                    init_map(df_req)
                else:
                    init_map(df_final)
        
    else:
        init_map(df_req)

def init_map(df_req):
       

    #iterate through all te locations
    length = len(df_req)

    if(length == 0):
        st.write("No services are available in this region.\n")

    m = folium.Map()
    df_req.apply(lambda row:folium.Marker(location=[row["Latitude"], row["Longtitude"]],
                                              radius=10, popup=folium.Popup('''<b><font size="+1">'''+str(row["Organization"])+'''</font></b><br><br>'''+str(row["Address"])+'''<br><br>'''+str(row["Phone"])+'''<br><br>'''+str(row["Rating"]),min_width=200, max_width=600, min_height=600, max_height=600),icon=folium.Icon(color='red',icon='star'), min_zoom = 20)
                                             .add_to(m), axis=1)

    sw = df_req[['Latitude', 'Longtitude']].min().values.tolist()
    ne = df_req[['Latitude', 'Longtitude']].max().values.tolist()
    m.fit_bounds([sw, ne]) 
    folium_static(m)

if __name__ == '__main__': 
    st.write("""
    # Map for Studentcare
    """)

    st.sidebar.header('Search Criteria')
    
    get_place_info()
