import re
import sys

import apiaccess
import constants

import streamlit as st
class AmbiguousAnswerException(Exception):
    pass


def read_input(prompt):
    """Displays appropriate prompt and reads the input.

    Args:
        prompt (str): String to be displayed.

    Returns:
        str: Stripped users input.

    """
    if prompt.endswith('?'):
        prompt = prompt + ' '
    else:
        prompt = prompt + ': '
    # print(prompt, end='', flush=True)
    
    
    # with st.chat_message("user"):
    #     st.markdown(prompt)
    return sys.stdin.readline().strip()
    # return prompt


def read_age_sex(user_input):
    """Reads age and sex specification such as "30 male".

    This is very crude. This is because reading answers to simple questions is
    not the main scope of this example. In real chatbots, either use some real
    intent+slot recogniser such as snips_nlu, or at least write a number of
    regular expressions to capture most typical patterns for a given language.
    Also, age below 12 should be rejected as our current knowledge doesn't
    support paediatrics (it's being developed but not delivered yet).

    Returns:
        int, str: Age and sex.

    """
    # answer = read_input("Please provide your age and gender in the following format: [age] [gender]\nFor example: 30 male\n\nNote: Ages below 12 and over 130 are not supported.\n")
    answer = read_input(user_input)
    
        
    
    
    try:
        age = int(extract_age(answer))
        sex = extract_sex(answer, constants.SEX_NORM)
        if age < constants.MIN_AGE:
            raise ValueError("Ages below 12 are not yet supported.")
        if age > constants.MAX_AGE:
            raise ValueError("Maximum possible age is 130.")
    except (AmbiguousAnswerException, ValueError) as e:
        print("{} Please repeat.".format(e))
        return read_age_sex(user_input)
    return age, sex


def read_complaint_portion(age, sex, auth_string, case_id, context, language_model=None):
    """Reads user input and calls the /parse endpoint of Infermedica API to
    extract conditions found in text.

    Args:
        age (dict): Patients age in {'value': int, 'unit': str} format.
        sex (str): Patients sex.
        auth_string (str): Authentication string.
        case_id (str): Case ID.
        context (list): List previous complaints.
        language_model (str): Chosen language model.

    Returns:
        dict: Response from /parse endpoint.
    Please describe your complaints. If you're done, simply press Enter.
    """
    text = read_input("Please describe you complaints. If you're done, simply press Enter")
    # with st.chat_message("assistant"):
    #     st.markdown(text)
    if not text:
        return None
    resp = apiaccess.call_parse(age, sex, text, auth_string, case_id, context,
                                language_model=language_model)
    
    print(resp)
    return resp.get('mentions', [])


def mention_as_text(mention):
    """Represents the given mention structure as simple textual summary.

    Args:
        mention (dict): Response containing information about medical concept.

    Returns:
        str: Formatted name of the reported medical concept, e.g. +Dizziness,
            -Headache.

    """
    _modality_symbol = {"present": "+", "absent": "-", "unknown": "?"}
    name = mention["name"]
    symbol = _modality_symbol[mention["choice_id"]]
    return "{}{}".format(symbol, name)


def context_from_mentions(mentions):
    """Returns IDs of medical concepts that are present."""
    return [m['id'] for m in mentions if m['choice_id'] == 'present']


def summarise_mentions(mentions):
    """Prints noted mentions."""
    print("Noting: {}".format(", ".join(mention_as_text(m) for m in mentions)))


def read_complaints(age, sex, auth_string, case_id, language_model=None):
    """Keeps reading complaint-describing messages from user until empty
    message is read (or just read the story if given). Will call the /parse
    endpoint and return mentions captured there.

    Args:
        age (dict): Patients age in {'value': int, 'unit': str} format.
        sex (str): Patients sex.
        auth_string (str): Authentication string.
        case_id (str): Case ID.
        lanugage_model (str): Chosen language model.

    Returns:
        list: Mentions extracted from user answers.

    """
    # with st.chat_message("assistant"):
    #         st.markdown("test")
    mentions = []
    context = [] 
    while True:
        portion = read_complaint_portion(age, sex, auth_string, case_id, context,
                                         language_model=language_model)
        # print(portion)
        # with st.chat_message("assistant"):
        #     st.markdown("portion")
            
        # with st.chat_message("assistant"):
        #     st.markdown(mentions)
        # with st.chat_message("assistant"):
        #     st.markdown(portion)
            
        if portion:
            summarise_mentions(portion)
            mentions.extend(portion)
            context.extend(context_from_mentions(portion))

        if mentions and portion is None:
            return mentions
    with st.chat_message("assistant"):
            st.markdown(context)
    # with st.chat_message("assistant"):
    #         st.markdown(portion)


def read_single_question_answer(question_text):
    """Primitive implementation of understanding user's answer to a
    single-choice question. Prompt the user with question text, read user's
    input and convert it to one of the expected evidence statuses: present,
    absent or unknown. Return None if no answer provided."""
    answer = read_input(question_text)
    if not answer:
        return None

    try:
        return extract_decision(answer, constants.ANSWER_NORM)
    except (AmbiguousAnswerException, ValueError) as e:
        print("{} Please repeat.".format(e))
        return read_single_question_answer(question_text)


def conduct_interview(evidence, age, sex, case_id, auth, language_model=None):
    """Keep asking questions until API tells us to stop or the user gives an
    empty answer."""
    question_number = 1
    while True:
        resp = apiaccess.call_diagnosis(evidence, age, sex, case_id, auth,
                                        language_model=language_model)
        question_struct = resp['question']
        diagnoses = resp['conditions']
        should_stop_now = resp['should_stop']
        if should_stop_now:
            triage_resp = apiaccess.call_triage(evidence, age, sex, case_id,
                                                auth,
                                                language_model=language_model)
            return evidence, diagnoses, triage_resp
        new_evidence = []
        if question_struct['type'] == 'single':
            question_items = question_struct['items']
            assert len(question_items) == 1
            question_item = question_items[0]
            observation_value = read_single_question_answer(
                question_text=f"{question_number}. {question_struct['text']}")
            if observation_value is not None:
                new_evidence.extend(apiaccess.question_answer_to_evidence(
                    question_item, observation_value))
        else:
            raise NotImplementedError("Group questions not handled in this"
                                      "example")
        evidence.extend(new_evidence)
        question_number += 1
    
    


def summarise_some_evidence(evidence, header):
    output_list = []  # Initialize an empty list to store the output
    output_list.append(header + ':')  # Append the header to the list
    for idx, piece in enumerate(evidence):
        output_list.append('{:2}. {}'.format(idx + 1, mention_as_text(piece)))  # Append each formatted string to the list
    output_list.append('')  # Append an empty string to represent the newline
    return output_list  # Return the list containing the output

def summarise_all_evidence(evidence):
    reported = []
    answered = []
    for piece in evidence:
        (reported if piece.get('initial') else answered).append(piece)
    # summarise_some_evidence(reported, '**Patient complaints**')
    patient_answer = summarise_some_evidence(answered, '**Patient answers**')
    return patient_answer


def summarise_diagnoses(diagnoses):
    print('**Diagnoses:**')
    for idx, diag in enumerate(diagnoses):
        print('{:2}. {:.2f} {}'.format(idx + 1, diag['probability'],
                                       diag['name']))
    print()


def summarise_triage(triage_resp):
    # print('**Triage level:** {}'.format(triage_resp['triage_level']))
    # teleconsultation_applicable = triage_resp.get(
    #     'teleconsultation_applicable')
    # if teleconsultation_applicable is not None:
    #     print('Teleconsultation applicable: {}'
    #           .format(teleconsultation_applicable))
    # print()
    triage_level = triage_resp['triage_level']
    return triage_level


def extract_keywords(text, keywords):
    """Extracts keywords from text.

    Args:
        text (str): Text from which the keywords will be extracted.
        keywords (list): Keywords to look for.

    Returns:
        list: All keywords found in text.

    """
    pattern = r"|".join(r"\b{}\b".format(re.escape(keyword))
                        for keyword in keywords)
    mentions_regex = re.compile(pattern, flags=re.I)
    return mentions_regex.findall(text)


def extract_decision(text, mapping):
    """Extracts decision keywords from text.

    Args:
        text (str): Text from which the keywords will be extracted.
        mapping (dict): Mapping from keyword to decision.

    Returns:
        str: Single decision (one of `mapping` values).

    Raises:
        AmbiguousAnswerException: If `text` contains keywords mapping to two
            or more different distinct decision.
        ValueError: If no keywords can be found in `text`.

    """
    decision_keywrods = set(extract_keywords(text, mapping.keys()))
    if len(decision_keywrods) == 1:
        return mapping[decision_keywrods.pop().lower()]
    elif len(decision_keywrods) > 1:
        raise AmbiguousAnswerException("The decision seemed ambiguous.")
    else:
        raise ValueError("No decision found.")


def extract_sex(text, mapping):
    """Extracts sex keywords from text.

    Args:
        text (str): Text from which the keywords will be extracted.
        mapping (dict): Mapping from keyword to sex.

    Returns:
        str: Single decision (one of `mapping` values).

    Raises:
        AmbiguousAnswerException: If `text` contains keywords mapping to two
            or more different distinct sexes.
        ValueError: If no keywords can be found in `text`.

    """
    sex_keywords = set(extract_keywords(text, mapping.keys()))
    if len(sex_keywords) == 1:
        return mapping[sex_keywords.pop().lower()]
    elif len(sex_keywords) > 1:
        raise AmbiguousAnswerException("I understood multiple sexes.")
    else:
        raise ValueError("No sex found.")


def extract_age(text):
    """Extracts age from text.

    Args:
        text (str): Text from which the keywords will be extracted.

    Returns:
        str: Found number (as a string).

    Raises:
        AmbiguousAnswerException: If `text` contains two or more numbers.
        ValueError: If no numbers can be found in `text`.

    """
    ages = set(re.findall(r"\b\d+\b", text))
    if len(ages) == 1:
        return ages.pop()
    elif len(ages) > 1:
        raise AmbiguousAnswerException("I understood multiple ages.")
    else:
        raise ValueError("No age found.")
