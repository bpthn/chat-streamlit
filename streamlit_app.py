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
# from symptom_checker import chat
import base64
import streamlit as st
from st_tabs import TabBar
# component1 = TabBar(tabs=["Home", "Group Members", "Project Background"], default=0)

# ================= OSHC =============================

df = pd.read_csv('merged_file_final.csv')
with open('intents_last_final.json', 'r') as file:
    answers_data = json.load(file)
# print(answers_data)
# Extract questions and tags
questions = df['Question'].tolist()
tags = df['Labels'].tolist()
# print(questions)
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
        icon=folium.Icon(color="orange"),
    ).add_to(m)

   # Add markers for nearest pharmacies with distance and name in the popup text
    for pharmacy, distance in nearest_pharmacies:
        popup_text = f"{pharmacy['pharmacy_name']} - Distance: {distance:.2f} km"
        folium.Marker(
            location=(pharmacy['latitude'], pharmacy['longitude']),
            icon=folium.Icon(color="blue"),
            popup=popup_text,
        ).add_to(marker_cluster)

    # Highlight the nearest pharmacy with a red icon and a popup with distance and name
    nearest_pharmacy, nearest_distance = nearest_pharmacies[0]
    nearest_pharmacy_location = (nearest_pharmacy['latitude'], nearest_pharmacy['longitude'])
    folium.Marker(
        location=nearest_pharmacy_location,
        popup=f"Nearest Pharmacy: {nearest_pharmacy['pharmacy_name']} - Distance: {nearest_distance:.2f} km",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    return m



# ------------------ STREAMLIT --------------------- #

# import streamlit as st
# from st_tabs import TabBar
# component1 = TabBar(tabs=["Home", "Group Members", "Project Background"], default=0)

# Function to set background image
def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .main {
        background-image: url("data:image/svg+xml;base64,%s");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
        height: 100vh;
    }
    
    
    </style>
    ''' % bin_str

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

# Function to get base64 encoding of binary file (for background image)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
        return base64.b64encode(data).decode()
    
def home_page():
    global chat_history
    # component1 = TabBar(tabs=["Home", "Group Members", "Project Background"], default=0)
    st.title("iChatOSHC")
    greeting = "Hi there! I'm iChatOSHC, here to assist you with your health and OSHC queries."
    chat_history = []
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Initialize menu choice
    if "menu_choice" not in st.session_state:
        st.session_state.menu_choice = None
        
    if "showSelect" not in st.session_state:
        st.session_state.showSelect = False
    
    if chat_history is None:
        chat_history = []

    # Display warning message for new users
    if st.session_state.menu_choice is None:
        st.warning("Welcome! 🌟 This app is easy to use, even if English isn't your first language. We're here to help with your health and OSHC questions. Feel free to ask anything! 🚀")
        greeting = "Hi there! I'm iChatOSHC, here to assist you."
    else:
        greeting = "Hi there! I'm iChatOSHC, here to assist you with your health and OSHC queries."

    # Instructions box
    with st.popover("See instructions 📝"):
        st.markdown("### How to Use")
        st.markdown("""
        To use the chatbot:\n
        1. Select one of the menu items: Diagnosis, OSHC, or Pharmacy Location.\n
        2. Follow the prompts or instructions provided.\n
        3. You can ask questions, seek diagnosis assistance, or find nearby pharmacies.\n
        4. Enjoy the chatbot experience!\n
        """)

        # Tips to Use
        st.markdown("### Tips to Use")
        st.markdown("""
        - Be specific and clear when asking questions or providing information.\n
        - Follow the format or instructions provided for each service.\n
        - If you encounter any issues, feel free to reach out for assistance.\n
        """)

    # Display warning messages for each menu option
    if st.session_state.menu_choice == 'Diagnosis':
        st.warning("Medical information provided by this API is for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a physician or qualified health provider for medical concerns.")
    elif st.session_state.menu_choice == 'Pharmacy Location':
        st.warning("This feature can currently help you find your nearest pharmacies located in New South Wales (NSW).")
    elif st.session_state.menu_choice == 'OSHC':
        st.warning("This chatbot provides information specifically for Bupa and Medibank OSHC policies. For information on other OSHC providers, please contact them directly.")

    # Display initial message
    with st.chat_message("assistant"):
        st.markdown(greeting)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    if not st.session_state.menu_choice:
        menu_choice = st.selectbox("What service are you looking for today?:", options=["Diagnosis", "OSHC", "Pharmacy Location"])
        if st.button("Submit"):
            st.session_state.menu_choice = menu_choice
            st.rerun()

    
    
    if st.session_state.menu_choice is not None and not st.session_state.showSelect:
        # Initialize the prompt message
        prompt_message = f"Ready to discuss {st.session_state.menu_choice}? Let's chat!"
    
        # Adjust the prompt message based on the menu choice
        if st.session_state.menu_choice == 'Diagnosis':
            prompt_message = "Please provide your age and gender in the following format: \n[age] [gender]. For example: 30 male."
        elif st.session_state.menu_choice == 'Pharmacy Location':
            prompt_message = "Where can I find the nearest pharmacy? Just share your address, and I'll help you locate the closest one!"
        elif st.session_state.menu_choice == 'OSHC':
            prompt_message = "Have a question about OSHC? Let's chat!"
        with st.chat_message("assistant"):
            st.markdown(prompt_message)
        # Set session state to prevent re-prompting
        st.session_state.showSelect = True
        st.session_state.messages.append({"role": "assistant", "content": prompt_message})
        chat_history.append({"role": "assistant", "content": prompt_message})
        # Display the assistant's initial prompt message
    

    user_input = None
                # Get user input based on the menu choice
    if st.session_state.menu_choice == 'Diagnosis':
        user_input = st.chat_input("What's your age and gender?")
    elif st.session_state.menu_choice == 'Pharmacy Location':
        user_input = st.chat_input("What's your address?")
    elif st.session_state.menu_choice == 'OSHC':
        user_input = st.chat_input("What's your OSHC question?")

    if user_input:
        # Display user input in chat message container
        with st.chat_message("user"):
            st.markdown(user_input) 
        response = None
            # Generate response based on the menu choice
        if st.session_state.menu_choice == 'OSHC':
            response = get_response(user_input)
  
        elif st.session_state.menu_choice == 'Diagnosis':
            response = "diagnosis"
        
            # Handle Pharmacy Location logic
        elif st.session_state.menu_choice == "Pharmacy Location":
            # Get the user's location from the address
            user_lat, user_lon = get_user_location(user_input)

            if user_lat and user_lon:
                user_location = (user_lat, user_lon)

                # Find the nearest pharmacies
                nearest_pharmacies = find_nearest_pharmacies((user_location), yellow_pages, top_n=10)

                if nearest_pharmacies:
                    response = "Here's the map with the nearest pharmacies and their distances."
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
                else:
                    st.error("No pharmacies found near your location.")
                    response = "No pharmacies found near your location."
            else:
                st.warning("Address not found. Please check and try again.")
                response = "Address not found. Please try again."

        # Display bot response in chat message container
        if response:
             with st.container():
                with st.chat_message("assistant"):
                        st.markdown(response)

        # Add user input and bot response to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})

        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        
    
    # Button to go back to the greeting page
    if st.session_state.menu_choice is not None or user_input:
        if st.button("Quit"):
            # Reset session state and rerun app
            st.session_state.messages = []
            st.session_state.menu_choice = None
            st.session_state.showSelect = False
            st.rerun()

def group_members_page():
    st.header("Meet The Creators", divider='rainbow')
    st.write('Master of Data Science and Innovation,University of Technology Sydeny ')
    st.image('iChatOSHC.svg', width=700)


def project_background_page():
    st.title("Project Background")
    st.subheader("Improving Healthcare Access for International Students in NSW")
    st.write(
        """
        New South Wales (NSW) welcomes millions of students from all over the world. If you're among them, you probably know about Overseas Student Health Cover (OSHC) insurance—it's essential for your visa requirements.

        Navigating healthcare in a new country can be challenging. Different languages, new healthcare systems, and not knowing where to go when you're sick or need medicine can be stressful. Our application aims to address these challenges.

        ### Our Solution

        We created a web-based application to help international students in NSW with their healthcare needs. Here's what it offers:

        1. **Symptom Diagnosis**: Using the Infermedica API, our application assesses symptoms to help you understand your health concerns. Note: this feature is currently in demo mode due to time-limited access to the API.

        2. **Location-Based Pharmacy Finder**: Find the top 10 nearby pharmacies by entering your home address. This ensures convenient access to medication.

        3. **OSHC Insurance Information**: We provide detailed information on Medibank and Bupa OSHC insurance policies, the most popular choices among international students in NSW. This helps you make informed decisions about your healthcare needs.

        We're excited to continue developing this application to make healthcare access easier for international students in NSW.
        """
    )


def main():
    # Set background image
    set_png_as_page_bg('Oversea Student Health Chatbot (Website)-2.svg') 

#    Create a sidebar with radio buttons for navigation
    # tab1, tab2, tab3 = st.tabs(["Home", "Group Members", "Project Background"])
    # with tab1:
    #     home_page()

    # with tab2:
    #     group_members_page()

    # with tab3:
    #     project_background_page()
        
        
    component1 = TabBar(tabs=["Home", "Group Members", "Project Background"], default=0)

    # Handle tab selection
    if component1 == 0:
        home_page()
    elif component1 == 1:
        group_members_page()
    elif component1 == 2:
        project_background_page()


if __name__ == "__main__":
    main()
