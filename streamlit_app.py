import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath("symptom_checker/conversation.py")))
sys.path.append(os.path.dirname(os.path.abspath("symptom_checker/apiaccess.py")))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.svm import SVC


import json


import joblib
import random
import json
import pandas as pd
from symptom_checker import chat

# ================= OSHC =============================

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

#================== location =======================
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from streamlit_chat import message  # For chatbot-like interaction

# Load your pharmacy data (example file path)
yellow_pages = pd.read_csv('yellow_pages_pharmacy_df.csv')

# Define the function to get user latitude and longitude from an address
def get_user_location(address):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Define the function to find the nearest pharmacies based on user location
def find_nearest_pharmacies(user_location, pharmacies, top_n=10):
    distances = []
    for _, pharmacy in pharmacies.iterrows():
        try:
            latitude = float(pharmacy['latitude'])
            longitude = float(pharmacy['longitude'])
            pharmacy_location = (latitude, longitude)
            distance = geodesic(user_location, pharmacy_location).kilometers
            distances.append((pharmacy, distance))
        except (ValueError, KeyError):
            continue  # Skip if latitude or longitude is invalid
    
    # Sort pharmacies by distance and return top N
    sorted_distances = sorted(distances, key=lambda x: x[1])
    return sorted_distances[:top_n]

# Function to create a Folium map with nearest pharmacies
def create_pharmacy_map(user_location, nearest_pharmacies):
    m = folium.Map(location=user_location, zoom_start=14)
    marker_cluster = MarkerCluster().add_to(m)

    # Add a marker for the user's location
    folium.Marker(
        location=user_location,
        popup="Your Location",
        icon=folium.Icon(color="green"),
    ).add_to(marker_cluster)

    # Add markers for nearest pharmacies
    for pharmacy, distance in nearest_pharmacies:
        popup_text = f"{pharmacy['pharmacy_name']} - Distance: {distance:.2f} km"
        folium.Marker(
            location=(pharmacy['latitude'], pharmacy['longitude']),
            icon=folium.Icon(color="blue"),
        ).add_to(marker_cluster)

    # Highlight the nearest pharmacy with a red icon
    nearest_pharmacy = nearest_pharmacies[0][0]
    folium.Marker(
        location=(nearest_pharmacy['latitude'], nearest_pharmacy['longitude']),
        popup=f"Nearest Pharmacy: {nearest_pharmacy['pharmacy_name']}",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    return m


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
      elif st.session_state.menu_choice == 'Pharmacy Location':
        txt = "Please enter your address:"
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
        
        if user_input.lower() == "quit":
          # Reset the session state if "quit" is entered
          st.session_state.messages = []
          st.session_state.menu_choice = None
          st.session_state.showSelect = False
          with st.chat_message("assistant"):
              st.markdown("Thanks for using the chatbot! Restarting...")
          st.experimental_rerun()  # Re-run after reset

          
        # Generate response based on the menu choice
        elif st.session_state.menu_choice == 'OSHC':
          response = get_response(user_input)
          # with st.chat_message("assistant"):
          #     st.markdown(f'OK {st.session_state.menu_choice}')
          # response = f'OK {st.session_state.menu_choice}'
        elif st.session_state.menu_choice == 'Diagnosis':
          # st.session_state.Diag is No
          response = chat.test(user_input)
        
        # Handle Pharmacy Location logic
        elif st.session_state.menu_choice == "Pharmacy Location":
            # Ask for the address
            with st.chat_message("assistant"):
                st.markdown("Please enter your address:")
    
            # Get the user's location from the address
            user_lat, user_lon = get_user_location(user_input)

            if user_lat and user_lon:
                user_location = (user_lat, user_lon)

                # Find the nearest pharmacies
                nearest_pharmacies = find_nearest_pharmacies((user_location), yellow_pages, top_n=10)

                if nearest_pharmacies:
                  # Create the map with nearest pharmacies
                  map_object = create_pharmacy_map(user_location, nearest_pharmacies)
                  folium_static(map_object)

                  # Display the top 10 nearest pharmacies in a table
                  nearest_pharmacies_df = pd.DataFrame(
                      [(pharmacy['pharmacy_name'], f"{distance:.2f} km") for pharmacy, distance in nearest_pharmacies],
                      columns=['Pharmacy Name', 'Distance (km)']
                  )
                  st.subheader("Top 10 Nearest Pharmacies:")
                  st.table(nearest_pharmacies_df)

                  # Add the response to the chat history
                  st.session_state.messages.append(
                      {"role": "assistant", "content": "Here's the map with the nearest pharmacies and their distances."}
                  )
                else:
                    st.error("No pharmacies found near your location.")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": "No pharmacies found near your location."}
                    )
            else:
                st.warning("Address not found. Please check and try again.")
                st.session_state.messages.append(
                    {"role": "assistant", "content": "Address not found. Please try again."}
                )
 
          
          
          
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
