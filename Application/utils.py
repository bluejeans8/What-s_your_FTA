import streamlit as st
import pandas as pd
import psycopg2
import hashlib
import chromadb
import openai
from openai import OpenAI
import pickle
from rank_bm25 import BM25Okapi
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())



# Security
#passlib,hashlib,bcrypt,scrypt
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

# DB connection
connection_info = "host=147.47.200.145 dbname=teamdb6 user=team6 password=qwer6 port=34543"
# connection_info = "host=localhost user=postgres dbname=postgres password=744744ks! port=5432"

def init_connection():
    return psycopg2.connect(connection_info)

def run_query(query):
    try:
        conn = init_connection()
        df = pd.read_sql(query, conn)
    except psycopg2.Error as e:
        print('DB error: ', e)
        conn.close()
    finally:
        conn.close()
    return df

def run_tx(query):
    try:
        conn = init_connection()
        with conn.cursor() as cur:
            cur.execute(query)
    except psycopg2.Error as e:
        print('DB error: ', e)
        conn.rollback()
        conn.close()
    finally:
        conn.commit()
        conn.close()
    return

def create_userstable():
    try:
        conn = init_connection()
        with conn.cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS userstable (userid TEXT, password TEXT,\
                        job TEXT, company TEXT, department TEXT, jobcontent TEXT, interest TEXT,\
                        PRIMARY KEY (userid))')
            
    except psycopg2.Error as e:
        print('DB error: ', e)
        conn.close()
    finally:
        conn.commit()
        conn.close()

# Insert information of newly signed up user to userstable(PostgreSQL DB)
def add_userdata(userid, password, job, company, department, jobcontent, interest):
    try:
        conn = init_connection()
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM userstable WHERE userid= '{userid}'")
            if cur.fetchall():  # 이미 userid가 존재한다면
                st.warning('User ID already exits')
            else:
                cur.execute(f"INSERT INTO userstable(userid, password, job, company, department, jobcontent, interest)\
                            VALUES ('{userid}', '{password}', '{job}', '{company}', '{department}', '{jobcontent}', '{interest}')")
                conn.commit()
                st.success("You have successfully created a valid Account")
                st.info('Go to Sign In menu to sign in')
    except psycopg2.Error as e:
        # 데이터베이스 에러 처리
        print("DB error: ", e)
        conn.rollback()
        conn.close()
    finally:
        conn.commit()
        conn.close()
    return

# function for Sign In
def login_user(userid, password):
    try:
        conn = init_connection()
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM userstable WHERE userid= '{userid}' AND password= '{password}'")
            data = cur.fetchall()   # row: (userid, password, job, company, department, jobcontent, interest) 형태
            
    except psycopg2.Error as e:
        print('DB error: ', e)
        conn.close()
    finally:
        conn.close()
    return data


# similar news search
def similar_news_search(user, query=None, num=1) :
    chroma_client = chromadb.PersistentClient(path=r".\data\chroma")
    collection = chroma_client.get_collection(name='FTA_collection')
    if query is not None:
        input_n = user + query
    else :
        input_n = user
    query_result = collection.query(query_texts=input_n, n_results=int(num))
    documents = query_result['documents'][0]
    News = pd.DataFrame(documents, columns=['Column'])
    return News

# bm25 preprocess
def preprocess_text(text):
    text = text.lower()
    word_tokens = word_tokenize(text)
    filtered_words = [word for word in word_tokens if word not in stopwords.words('english')]
    return filtered_words

# similar agreement search
def similar_agreement_search(user, query=None) :
    
    agreements = []
    with open(r'.\data\joined_chunks.pkl', 'rb') as file:
        agreements_5000 = pickle.load(file)

    with open(r".\data\agreements_bm25_5000.pkl", 'rb') as file :
        bm25 = pickle.load(file)
        if query is not None:
            input_a = user + query
        else :
            input_a = user
            
        preprocessed_query = preprocess_text(input_a)
        doc_scores = bm25.get_scores(preprocessed_query)
        max_score_index = doc_scores.argmax()
        Agreements = agreements_5000[max_score_index]
    return Agreements


# function for chatbot service
client = OpenAI()
def chatbot_answer(question, model="gpt-4-1106-preview"):
    

    response = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question}
        ],
        max_tokens=1500
    )

    return response.choices[0].message.content
# 

    
