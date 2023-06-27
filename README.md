# Evernote AI Chatbot Powered by Apaceh NiFi 2.0, OpenAI, Pinecone and LangChain

## Use Case Context

Evernote, a leading and powerful note-taking tool, can be a labyrinth of text, documents, images, and audio recordings accumulated over time. Navigating and exploring this vast collection of notes can be challenging.

This projects shows how to create a chat-like AI interface to Evernote  leveraging the highly anticipated Apache NiFi 2.0 release and its seamless Python integration and various generative AI tools. It focuses on rapidly creating AI data pipelines with Apache NiFi, seamlessly integrating various AI ecosystem technologies, such as OpenAI, Pinecone, and LangChain. 

AFter you setup the NIFi flows as per the instructions in this project, you will be able have these types conversational experience your Evernote.

[![Evernote Chabbot Conversation](https://img.youtube.com/vi/RRMlWvh4ha0/0.jpg)](https://www.youtube.com/watch?v=RRMlWvh4ha0)


## Pre-requisite  / Setup

1. Install Python 3.9. You will need this to run Python processors in NiFi as well as the stream-lit chat web app
2. Build Apache NiFi 2.0 Snapshot release or download it from [here](https://drive.google.com/file/d/1xAuao9rV8F_CQBLqWLWp7P12iZpuuUEP/view?usp=drive_link) into this location $NIFI_HOME
   - Confiugure NiFi
     - modify the $NIFI_HOME/confi/nifi.poperties for the following properties
       - nifi.python.command=<<Set to location of your python 3.8 install>>
         - e.g:  nifi.python.command=/opt/homebrew/Cellar/python@3.9/3.9.17/bin/python3.9
       - nifi.python.extensions.source.directory.dev=<<Set to the location of the custom python processors in this git repo located under nifi-processor)
         - e.g: If you clone this repo to folder evernote-ai-chat-bot, then ti woudl be: nifi.python.extensions.source.directory.dev=/evernote-ai-chatbot/nifi-processor
2. Signup for a free account on [Pinecone](https://www.pinecone.io/) and create an index through the console or the SDK. Save your Pinecone API key information. See the [Pinecone Quickstart Guide](https://docs.pinecone.io/docs/quickstart). You will need these to store and retrieve your vector embeddings of your Evernote notes. 
3. Create an account on [OpenAI](https://platform.openai.com/) and create a secret API key. You will need this to to work with OpenAI embeddings model to vector embeddings and their LLM models.
5. Install the following python packages: 
   - s
6. sdsd
7. 


