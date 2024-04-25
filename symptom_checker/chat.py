import os
import sys
sys.path.append(os.path.dirname('conversation.py'))
sys.path.append(os.path.dirname('apiaccess.py'))
import streamlit as st



API_KEY = "15b17c76:0da83aaa8dc67bf00f8778c56c759e33"

import argparse
import uuid

import conversation
import apiaccess


def get_auth_string(auth_or_path):
    """Retrieves authentication string from string or file.

    Args:
        auth_or_path (str): Authentication string or path to file containing it

    Returns:
        str: Authentication string.

    """
    if ":" in auth_or_path:
        return auth_or_path
    try:
        with open(auth_or_path) as stream:
            content = stream.read()
            content = content.strip()
            if ":" in content:
                return content
    except FileNotFoundError:
        pass
    raise ValueError(auth_or_path)


def new_case_id():
    """Generates an identifier unique to a new session.

    Returns:
        str: Unique identifier in hexadecimal form.

    Note:
        This is not user id but an identifier that is generated anew with each
        started "visit" to the bot.

    """
    return uuid.uuid4().hex


def parse_args():
    """Parses command line arguments.

    Returns:
        argparse.Namespace: Namespace containing three public attributes:
            1. auth (str) - authentication credentials.
            2. model (str) - chosen language model.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth",
                        default=API_KEY,
                        help="authentication string for Infermedica API: "
                             "APP_ID:APP_KEY or path to file containing it.")
    parser.add_argument("--model",
                        help="use non-standard Infermedica model/language, "
                             "e.g. infermedica-es")
    args = parser.parse_args()
    return args

def print_diagnoses_summary(diagnoses):
    print("Diagnoses:")
    diagnoses_summary = []
    for diag in diagnoses:
        diagnoses_summary.append("{} ({:.2f}%)".format(diag['name'], diag['probability']*100))
    print(", ".join(diagnoses_summary[:-1]) + ", and " + diagnoses_summary[-1] + ".")


def run(user_input):
    """Runs the main application."""
    # with st.chat_message("assistant"):
    #     st.markdown("in run")
    conversation.read_input(user_input)
    # with st.chat_message("assistant"):
    #     st.markdown('in run')
    
    args = parse_args()
    auth_string = get_auth_string(args.auth)
    case_id = new_case_id()

    age, sex = conversation.read_age_sex(user_input)
    # print(f"Ok, {age} year old {sex}.")
    age = {'value':  age, 'unit': 'year'}
    # with st.chat_message("assistant"):
    #     st.markdown(age)
    print()
    
    naming = apiaccess.get_observation_names(age, auth_string, case_id, args.model)
    # with st.chat_message("assistant"):
    #     st.markdown(naming)
    with st.chat_message("assistant"):
        st.markdown(age)
    mentions = conversation.read_complaints(age, sex, auth_string, case_id, args.model)
    with st.chat_message("assistant"):
        st.markdown(mentions)
    evidence = apiaccess.mentions_to_evidence(mentions)
    print()
    # print("Before we proceed with symptom diagnosis, please answer the following questions with 'y' for yes or 'n' for no:")
    txt = "Before we proceed with symptom diagnosis, please answer the following questions with 'y' for yes or 'n' for no:"
    with st.chat_message("assistant"):
        st.markdown(txt)
    evidence, diagnoses, triage = conversation.conduct_interview(evidence, age,
                                                                 sex, case_id,
                                                                 auth_string,
                                                                 args.model)

    apiaccess.name_evidence(evidence, naming)

    print()
    patient_answer = conversation.summarise_all_evidence(evidence)
    print_diagnoses_summary(diagnoses)
    print()
    # conversation.summarise_diagnoses(diagnoses)
    triage_level = conversation.summarise_triage(triage)
    triage_messages = {
    "emergency_ambulance": "Emergency: Call an ambulance now",
    "emergency": "Emergency: Go to the nearest emergency department or call an ambulance",
    "consultation_24": "Urgent Consultation: See a doctor within 24 hours",
    "consultation": "Consultation: Schedule an appointment with a doctor",
    "self_care": "Self-care: Monitor symptoms and consult a doctor if they worsen"
    }
    with st.chat_message("assistant"):
        st.markdown(f"Considering the likelihood of {diagnoses[0]['name']} and the symptoms you've described.")
        st.markdown(f"It's recommended that you take a {triage_messages[triage_level]}.")
        st.markdown("")
        st.markdown("")
        st.markdown("Please note that this symptom diagnosis is a guide and should not be solely relied upon.")
        st.markdown("If you have any concerns or if your symptoms worsen, consider seeking medical attention from a healthcare provider.")
        
    print(f"Considering the likelihood of {diagnoses[0]['name']} and the symptoms you've described.")
    print(f"It's recommended that you take a {triage_messages[triage_level]}.")
    print("")
    print("")
    print("Please note that this symptom diagnosis is a guide and should not be solely relied upon.")
    print("If you have any concerns or if your symptoms worsen, consider seeking medical attention from a healthcare provider.")
    
def test(user_input):
    # with st.chat_message("assistant"):
    #     st.markdown('in test')
   
    run(user_input)
     
    
# if __name__ == "__main__":
#     run()