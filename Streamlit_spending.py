import streamlit as st
import json 
import requests
import pandas as pd
import numpy as np
import datetime
from datetime import date


#Initial setup and title of Webapp
st.title("Federal Spending Data")

#setting spending type selector
spending_type_var=st.sidebar.selectbox('Spending Type',('General','Disaster Emergency Funds'))


if spending_type_var=='General': #General tab

    # Selection portion
    state_dict={"Arkansas":"AR","Louisiana":"LA","Oklahoma":"OK","New Mexico":"NM","Texas":"TX"}
    state_var=st.sidebar.selectbox("State",(list(state_dict.keys())))
    start_date_var=st.sidebar.date_input('Start Date',datetime.date(2020, 1, 1))
    end_date_var=st.sidebar.date_input('End Date',datetime.date(2021, 1, 1))
    


    # Setting up the General API  call   
    payload=  {"scope":"place_of_performance",
            "geo_layer":"county",
            "filters":{
                "place_of_performance_locations":[{"country":"USA","state":state_dict[state_var]}],
                "time_period":[
                    {"start_date":str(start_date_var),"end_date":str(end_date_var)}]}
            }

    header = {"Content-Type": "application/json"}

    response=requests.post("https://api.usaspending.gov/api/v2/search/spending_by_geography/",headers=header, json=payload)
    response=json.loads(response.text)
    funds_received=pd.DataFrame()

    try:
        len(response['results'])
    except:
        None
        
    for i in response['results']:
        funds_received=funds_received.append(i,ignore_index=True)
        
    # insert error messages
    today_info=date.today()
    today_info = today_info.strftime("%Y-%m-%d")

    if  datetime.datetime.strptime(str(start_date_var),"%Y-%m-%d")<= datetime.datetime.strptime(str('2015-01-01'),"%Y-%m-%d"):
        st.write("Invalid Start Date - Please include a date after 2015-01-01")

    elif  datetime.datetime.strptime(str(end_date_var),"%Y-%m-%d")> datetime.datetime.strptime(str(today_info),"%Y-%m-%d"):
        st.write("Invalid End Date - Please include a date prior to",today_info)

    else:
        #show table
        try:
            funds_received=funds_received[funds_received['display_name'].notnull()] #drop null values
            funds_received=funds_received.sort_values(by=['display_name'],ascending=True) #setting in descending order
            funds_received=funds_received.rename(columns={'aggregated_amount':"Aggregated Amount","per_capita":"Per Capita","display_name":"County"}) #changing names
            funds_received=funds_received[['Aggregated Amount','County']].set_index('County') #setting index
            st.write("Spending by County in the state of ",state_var)
            st.write("You are viewing spending dates between ",start_date_var," and ", end_date_var)            
            st.table(funds_received.style.format({"Aggregated Amount": "${0:,.2f}","Per Capita": "${0:,.2f}"}))  #formatting words
            #st.table(funds_received[["Aggregated Amount","County"]].style.format({"Aggregated Amount": "${0:,.2f}"}))  #formatting words
    
            
        except:
            st.write('Please make a selection')



# Using the Disaster api section 

if spending_type_var=='Disaster Emergency Funds':
    #selection options
    state_dict={"Arkansas":"AR","Louisiana":"LA","Oklahoma":"OK","New Mexico":"NM","Texas":"TX"}
    state_var=st.sidebar.selectbox("State",(list(state_dict.keys())))
    def_codes_dict={"Coronavirus Preparedness and Response Supplemental Appropriations Act, 2020":"L",
                    "Families First Coronavirus Response Act":"M",
                    "Coronavirus Aid, Relief, and Economic Security Act or the CARES Act":"N",
                    "Coronavirus Aid, Relief, and Economic Security Act or the CARES Act | Paycheck Protection Program and Health Care Enhancement Act":"O",
                    "Paycheck Protection Program and Health Care Enhancement Act":"P",
                    "Future Disaster and P.L. To Be Determined":"R"}    
    def_codes_var= st.sidebar.selectbox("Disaster Emergency Fund Code", (list(def_codes_dict.keys())))

    # Setting up the General API  call   
    payload=  {"filter":
        {
        "def_codes":[def_codes_dict[def_codes_var]]
        },
        "geo_layer":"state",
        "geo_layer_filters":[state_dict[state_var]],
        "spending_type":"obligation"}

    header = {"Content-Type": "application/json"}

    response=requests.post("https://api.usaspending.gov/api/v2/disaster/spending_by_geography/",headers=header, json=payload)
    response=json.loads(response.text)
    funds_received=pd.DataFrame()

    try:
        len(response['results'])
    except:
        None
        
    for i in response['results']:
        funds_received=funds_received.append(i,ignore_index=True)
    
    #generating and displaying table
    try:
        funds_received=funds_received.rename(columns={'amount':"Amount","award_count":"Award Count", "display_name":"State"})
        funds_received=funds_received[['Amount','Award Count','State']].set_index('State')
        st.write('Spending Associated with ', def_codes_var)
        st.table(funds_received.style.format({"Amount": "${0:,.2f}","Award Count":"{0:,.0f}"}))
        st.write("Data for Disaster Emergency Funds are based on values through November 30, 2020 - please visit usaspending.gov for further updates")
    except:
        st.write("")


#final notes


st.sidebar.write('This page utilizes information from the USAspending.gov website to show federal spending within the states of Arkansas,Louisiana,Oklahoma,New Mexico and Texas.')
st.sidebar.markdown("Source:https://www.usaspending.gov")










