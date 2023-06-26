import streamlit as st
from streamlit_chat import message

# Setting page title and header
st.set_page_config(page_title="Evernote Semenatic Search", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>Evernote AI Chatbot Powered by Apache NiFi using OpenAI, Pinecone & Langchain</h1>", unsafe_allow_html=True)

import requests

API_ENDPOINT = "http://127.0.0.1:9898/evernotechatbot"


# Initialise session state variables
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []


# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Sidebar")
counter_placeholder = st.sidebar.empty()
clear_button = st.sidebar.button("Clear Conversation", key="clear")


# reset everything
if clear_button:
    st.session_state['chat_history'] = []


def generate_response(query, chat_history):

    # Convert the chat_history tuple array into a single string\
    chat_history_string = None
    print(chat_history)
    if chat_history:
        # chat_history_string = ', '.join([f"('{x}', '{y}')" for x, y in chat_history])
        #chat_history_string = ' '.join([f'({item[0]}, {item[1]})' for item in chat_history])
        chat_history_string = ' '.join([f'("{item[0]}", "{item[1]}")' for item in chat_history])

        print("Chat hisotry as string is: " + chat_history_string)


    params = {
        "question": query,
        "chat_history": chat_history_string
    }
    response = requests.post(API_ENDPOINT, params=params)
    response.raise_for_status()

    return response.text

def parse_response(response):

    if 'SOURCES' in response:

        answer, source = response.split('SOURCES', 1)
        return {"answer": answer, "source": source}
    else:
        return {"answer" : response, "source" : ''}




# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        chat_history = st.session_state['chat_history']
        response = generate_response(user_input, chat_history)
        chat_history.append((user_input, response))


if st.session_state['chat_history']:
    with response_container:
        for index, tuple_items in enumerate(st.session_state['chat_history']):
            question = tuple_items[0]
            answer = tuple_items[1]
            answer_and_source = parse_response(answer)
            message(question, is_user=True, key=str(index) + '_user')
            message(answer_and_source['answer'], key=str(index))
            source = answer_and_source['source']
            # if  source is not None and len(source) > 0 and source != ':' and question != 'What can you help with?' :
            if source is not None and len(source) > 0 and source != ':' :
                st.write(
                    f"Evernote Source: {answer_and_source['source']}")



