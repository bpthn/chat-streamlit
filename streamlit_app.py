import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath("symptom_checker/conversation.py")))
sys.path.append(os.path.dirname(os.path.abspath("symptom_checker/apiaccess.py")))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.svm import SVC


import json


import matplotlib.pyplot as plt
import joblib
import random
import json
import pandas as pd
from symptom_checker import chat


df = pd.read_csv('merged_file.csv')
with open('Final_intents.json', 'r') as file:
    answers_data = json.load(file)
# print(answers_data)
# Extract questions and tags
questions = df['Question'].tolist()
tags = df['Labels'].tolist()
    
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(questions)

# Train model
clf = SVC()
clf.fit(X, tags)


def get_prediction(user_input):
    user_vector = vectorizer.transform([user_input])
    tag = clf.predict(user_vector)[0]
    return tag

def get_response(user_input):
    tag = get_prediction(user_input)
    responses = [intent["responses"] for intent in answers_data['intents'] if intent["tag"] == tag]
    if responses:
        response = random.choice(responses[0])  # Randomly select a response from the list of responses
    else:
        response = "I'm sorry, I don't have an answer for that."
    return response


# ------------------ STREAMLIT --------------------- #

import streamlit as st


# Add the necessary imports and function definitions here
chat_history = []

def main():
    global chat_history
    st.title("Streamlit Chat")
    greeting = "Hi, how can I help you? Choose from menu items Diagnosis, OSHC, or Pharmacy Location."
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Initialize menu choice
    if "menu_choice" not in st.session_state:
        st.session_state.menu_choice = None
        
    if "showSelect" not in st.session_state:
      st.session_state.showSelect = False
    
    # if chat_history is None:
    #   chat_history = []
    
        
        
    # Display initial message
    with st.chat_message("assistant"):
        st.markdown(greeting)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    if not st.session_state.menu_choice:
        menu_choice = st.selectbox("Select a menu item:", options=["Diagnosis", "OSHC", "Pharmacy Location"])
        if st.button("Submit"):
            st.session_state.menu_choice = menu_choice
            print(st.session_state)
            # st.empty()
            
            # with st.chat_message("assistant"):
            #   st.markdown(f'OK {st.session_state.menu_choice}')
            # Perform any actions you want after submission
            
            st.experimental_rerun()

   
          
    # if st.session_state.menu_choice:
    #   with st.chat_message("assistant"):
    #     st.markdown(f'OK {st.session_state.menu_choice}')
    user_input = None
    if st.session_state.menu_choice is not None and st.session_state.showSelect is False:
      response = f'Ask about {st.session_state.menu_choice}'
      # with st.chat_message("assistant"):   
      #   st.markdown(response)
      if st.session_state.menu_choice == 'Diagnosis':
        txt = "Please provide your age and gender in the following format: [age] [gender]\nFor example: 30 male\n\nNote: Ages below 12 and over 130 are not supported.\n"
        response = txt
      with st.chat_message("assistant"):   
        st.markdown(response)
      st.session_state.showSelect = True
      st.session_state.messages.append({"role": "assistant", "content": response})
    if st.session_state.menu_choice is not None:
      user_input = st.chat_input("What's up?")
      
    if user_input:
        # Display user input in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)
        
        if user_input == 'quit':
          
          
          
          st.session_state.messages = []
          st.session_state.menu_choice = None
          st.session_state.showSelect = False
          response = 'Thanks'
          print(chat_history)
          st.experimental_rerun()
          
        # Generate response based on the menu choice
        elif st.session_state.menu_choice == 'OSHC':
          response = get_response(user_input)
          # with st.chat_message("assistant"):
          #     st.markdown(f'OK {st.session_state.menu_choice}')
          # response = f'OK {st.session_state.menu_choice}'
        elif st.session_state.menu_choice == 'Diagnosis':
          # st.session_state.Diag is No
          response = chat.test(user_input)
        else:
            # Call get_response() function for other menu items
            response = 'no'

        # Display bot response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add user input and bot response to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        print(chat_history)
# Add the OSHC_chatbot() function here if needed

if __name__ == "__main__":
    
    main()
