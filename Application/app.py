import streamlit as st
import time
import pandas as pd
import numpy as np
import psycopg2
from utils import *
import pickle
from rank_bm25 import BM25Okapi
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import openai
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


st.title('Find Your FTA Contents')
st.write('Recommendation & Chatbot service for FTA related contents')


signin, signup, service = st.tabs(['Sign In', 'Sign Up', 'service'])

with signin:
    # Sign In tab
    st.subheader('Sign In')
    
    # 로그인 상태를 추적하는 플래그가 설정되어 있지 않으면 로그인 폼을 표시
    if not st.session_state.get('logged_in'):
        userid = st.text_input('ID:')
        password = st.text_input('Pswd', type='password')

        if st.button('Sign In'):
            create_userstable()
            hashed_pswd = make_hashes(password)

            result = login_user(userid, check_hashes(password, hashed_pswd))
            if result:
                st.success('Logged In as {}'.format(userid))
                st.session_state['logged_in'] = True
                st.subheader('These are some contents you would like...')
                st.write()
        
                with st.spinner('Please wait...'):
                    # result -> [(userid, password, job, company, department, jobcontent, interest)]
                    per_info = list(result[0])[2:]   # per_info = ex) ['public officer', 'MOTIE', 'east asia divison', 'economic cooperate with ASEAN and India', 'AI regulation']
                    per_info_txt = ', '.join(per_info) # per_info 컴마로 구분된 하나의 텍스트로 합치기
                    st.session_state['per_info_str'] = per_info_txt
                    print(st.session_state['per_info_str'])
                    personal_recommendation = similar_news_search(per_info_txt) # user에 따른 뉴스 추천
                    print(personal_recommendation)
                    st.write(personal_recommendation.iloc[0][0])  # 추천기사 출력
                    time.sleep(5)
                st.success('Done!')

            else:
                st.warning('Incorrect User ID or Password')
                
    if st.session_state.get('logged_in'):
        st.write("You are logged in.")

with signup:
    # Sign Up tab
    st.subheader('Create New Account')

    userid = st.text_input('User ID:')
    password = st.text_input('Password:', type='password')
    job = st.text_input('Job:')
    company = st.text_input('Company:')
    department = st.text_input('Department:')
    jobcontent = st.text_input('Job Content:')
    interest = st.text_input('Current Interest:')

    if st.button('Sign Up'):
        create_userstable()
        add_userdata(userid, make_hashes(password), job, company, department, jobcontent, interest)

with service:
    # service tab
    st.sidebar.title('Service Category')
    select_service = st.sidebar.selectbox(
        'Choose service to use.', 
        ['---SELECT---', 'Contents Recommendation', 'Chat with Chatbot'])

    if str(select_service) == 'Contents Recommendation':
        st.header(select_service)
        st.write()
        text = st.text_area(label='Input the keywords or contents that are related to what you want to find.',
                            placeholder='ex) international dispute division')
        num = st.text_area(label='Input the number of contents you want to find.',
                        placeholder='ex) 3')
        
        if st.button('Search'):
            if 'per_info_str' in st.session_state:
                with st.spinner('Please wait...'):
                    print(st.session_state['per_info_str'])
                    recommendation = similar_news_search(st.session_state['per_info_str'], text, num)
                    st.dataframe(recommendation)
                    time.sleep(5)
            
            st.success('Done!')

    elif str(select_service) == 'Chat with Chatbot':
        st.header(select_service)
        st.subheader('How can I help you today?')
        st.write()
        text = st.text_area(label='Ask to Chatbot...',
                            placeholder='ex) Recommend some FTA contents related to international dispute division.')
        if 'per_info_str' in st.session_state:
            News = similar_news_search(st.session_state['per_info_str'], text)
            Agreement = similar_agreement_search(st.session_state['per_info_str'], text)
        question_full = f'''

You will receive the agreement and news data that are most relevant to the question as context. Before answering, quote the relevant sentence in the agreement and news, as in word-by-word, before answering.

[Context]:

<<User>>

{st.session_state['per_info_str']}

<<Agreement>>

{Agreement}

<<News>>

{News}

[Question]:

{text}

[Answer]:

'''

        #question_full = '<User>' + st.session_state['per_info_str'] + '<Query>' + text + '<Agreement>' + Agreement + '<News>' + News
        #question_full = question_full['Column'].str.cat(sep='\n')
        print(question_full)
        if st.button('Ask'):
            with st.spinner('Please wait...'):
                answer = chatbot_answer(question_full)
                st.write(answer)
                time.sleep(5)
            st.success('Done!')

    else:
        st.header('Our ongoing service: ')

        st.subheader('Contents Recommendation Service')
        st.write('You can now easily get the FTA contents that you want ro find!')
        st.subheader('Chat with Chatbot Service')
        st.write('Start chatting with Chatbot and get what you want!')
        st.subheader('Recommendation based on User Info')
        st.write('You can get some contents related to you personal info')





