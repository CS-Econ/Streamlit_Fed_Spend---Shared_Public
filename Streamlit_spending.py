import streamlit as st
import json 
import requests
import pandas as pd
import numpy as np
import datetime
from datetime import date


#Initial setup and title of Webapp
st.title("Feederal Spending Data")
#setting spending type
spending_type_var=st.sidebar.selectbox('Spending Type',('General','Disaster Emergency Funds'))

#################################
#General Tab
#################################
if spending_type_var=='General': #General tab

    # Selection portion dictionaries
    state_dict={"Arkansas":"AR","Louisiana":"LA","Mississippi":"MS","New Mexico":"NM","Texas":"TX"}
    recipient_type_dict={"All Business Recipients":'category_business','Small Business':'small_business',"Other Than Small Business":"other_than_small_business",
                        'Minority Owned Business':'minority_owned_business',"Sole Proprietorship":'sole_proprietorship',
                        'Manufacturer of Goods':'manufacturer_of_goods',
                        'Women Owned Business':'woman_owned_business',
                        'Veteran Owned Business':'veteran_owned_business','Small Business':'small_business'}
    #buttons
    state_var=st.sidebar.selectbox("State",(list(state_dict.keys())))
    start_date_var=st.sidebar.date_input('Start Date',datetime.date(2020, 1, 1))
    end_date_var=st.sidebar.date_input('End Date',datetime.date(2021, 1, 1))
    recipient_type_var=st.sidebar.multiselect('Choose Business Recipient Types',(list(recipient_type_dict.keys())))
    #################################################
    ### Setting up the recipient_type_selection based on multi-criteria
    recipient_type_selection=(recipient_type_var)
    recipient_type_response=["None"] #Response that will be send to recipient_type_names (recipient_type_selection_activator)
    #recipient_type_response_dict=""
    recipient_type_selection_count=len(recipient_type_var)
    if recipient_type_selection_count==0:   #this turns off the recipient selection if there is no selection
        recipient_type_selection_activator=None 
    if recipient_type_selection_count>=1: #this activates the selection for recipient selection
        recipient_type_selection_activator="recipient_type_names"
        i=0
        while i<recipient_type_selection_count:
            #getting the dictionary keys
            recipient_type_dict_response=recipient_type_dict[recipient_type_var[i]]#response from the dictionary
            recipient_type_response.append(recipient_type_dict_response)
            i+=1
             


    ###################################
    # Setting up the General API  call   
    payload=  {"scope":"place_of_performance",
            "geo_layer":"county",
            "filters":{
                "place_of_performance_locations":[{"country":"USA","state":state_dict[state_var]}],
                #"recipient_type_names":['minority_owned_business',"woman_owned_business",'small_business'],           
                recipient_type_selection_activator:recipient_type_response,
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

    if  datetime.datetime.strptime(str(start_date_var),"%Y-%m-%d")<= datetime.datetime.strptime(str('2015-01-01'),"%Y-%m-%d"): #error for older date
        st.write("Invalid Start Date - Please include a date after 2015-01-01")

    elif  datetime.datetime.strptime(str(end_date_var),"%Y-%m-%d")> datetime.datetime.strptime(str(today_info),"%Y-%m-%d"):#error for date after current date
        st.write("Invalid End Date - Please include a date prior to",today_info)

    else: #valid entry
        #show table
        try:
        #funds_received['aggregated_amount']=(funds_received['aggregated_amount'].round(decimals=2)).apply(str) #turning into a string 
        #funds_received['aggregated_amount']=funds_received['aggregated_amount'].astype(float).replace(',','.').astype(float)
        #st.table(funds_received[['aggregated_amount','display_name']])
            funds_received=funds_received[funds_received['display_name'].notnull()] #drop null values
            funds_received=funds_received.sort_values(by=['display_name'],ascending=True) #setting in descending order
            funds_received=funds_received.rename(columns={'aggregated_amount':"Aggregated Amount","display_name":"County"}) #changing names
            funds_received=funds_received[['Aggregated Amount','County']].set_index('County') #setting index
            st.write("Spending by County in the state of ",state_var)
            st.write("You are viewing spending dates between ",start_date_var," and ", end_date_var)
            #specific section for recipient_selection >=1 
            if recipient_type_selection_count>=1: 
                #if 'All Business Recipients' in recipient_type_var: #message for ALL Business recipients
                #    empty_string=", "
                #    st.write('You have selected All Business Recipients')
                #else: #Message for all other businesses
                empty_string=", "
                st.write('You have selected the following business recipients: ',empty_string.join(recipient_type_var))

            st.table(funds_received.style.format({"Aggregated Amount": "${0:,.2f}"}))  #formatting words on table
            #st.table(funds_received[["Aggregated Amount","County"]].style.format({"Aggregated Amount": "${0:,.2f}"}))  #formatting words
    
            
        except:
            st.write('Please make a selection')

   

#########################################
# Using the Disaster api section 
#########################################
if spending_type_var=='Disaster Emergency Funds':
    #selection options
    state_dict={"Arkansas":"AR","Louisiana":"LA","Mississippi":"MS","New Mexico":"NM","Texas":"TX"}
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


st.sidebar.write('This page utilizes information from the USAspending.gov website to show federal spending within the states of Arkansas,Louisiana,Mississippi,New Mexico and Texas.')
st.sidebar.markdown("Source:https://www.usaspending.gov")










