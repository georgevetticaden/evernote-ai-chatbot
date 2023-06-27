# Evernote AI Chatbot Powered by Apaceh NiFi 2.0, OpenAI, Pinecone and LangChain

## Use Case Context

Evernote, a leading and powerful note-taking tool, can be a labyrinth of text, documents, images, and audio recordings accumulated over time. Navigating and exploring this vast collection of notes can be challenging.

This projects shows how to create a chat-like AI interface to Evernote  leveraging the highly anticipated Apache NiFi 2.0 release and its seamless Python integration and various generative AI tools. It focuses on rapidly creating AI data pipelines with Apache NiFi, seamlessly integrating various AI ecosystem technologies, such as OpenAI, Pinecone, and LangChain. 

AFter you setup the NIFi flows as per the instructions in this project, you will be able have these types conversational experience your Evernote.

[![Evernote Chabbot Conversation](https://img.youtube.com/vi/RRMlWvh4ha0/0.jpg)](https://www.youtube.com/watch?v=RRMlWvh4ha0)


## Prerequisites  / Setup

1. Install Python 3.9 to location $PYTHON_HOME 
   - You will need this to run NiFi Python processors  and stream-lit chatbot web app. Install the following modules in your Python virtual env to run the web app:
      - streamlit
      - streamlit-chat
2. Clone this repo to location $EVERNOTE_CHAT_BOT. 
   - You will need to refer to the custom Python processors in this repo in the the nifi.properties 
3. Build Apache NiFi 2.0 Snapshot release 
   - Build it yourself from the [Apache NiFi Git Repo](https://github.com/apache/nifi) or download it from [here](https://drive.google.com/file/d/1xAuao9rV8F_CQBLqWLWp7P12iZpuuUEP/view?usp=drive_link) into this location $NIFI_HOME 
4. Confiugure NiFi
     - Modify the $NIFI_HOME/confi/nifi.poperties for the following properties
       - nifi.python.command=$PYTHON_HOME
         - e.g:  nifi.python.command=/opt/homebrew/Cellar/python@3.9/3.9.17/bin/python3.9
       - nifi.python.extensions.source.directory.dev=$EVERNOTE_CHAT_BOT/nifi-processor
         - e.g: If you clone this repo to folder evernote-ai-chat-bot, then it woudl be: nifi.python.extensions.source.directory.dev=/evernote-ai-chatbot/nifi-processor
5. Start NiFi
   - Follow the instructions to start NIFi: [Starting NiFi](https://nifi.apache.org/docs/nifi-docs/html/getting-started.html#starting-nifi)
   - Configure credentials and access the NiFi UI by following the instructions:  [I started NIFi, Now what?](https://nifi.apache.org/docs/nifi-docs/html/getting-started.html#starting-nifi)
6. Signup for a free account on [Pinecone](https://www.pinecone.io/) and create an index through the console or the SDK. Save your Pinecone API key information. See the [Pinecone Quickstart Guide](https://docs.pinecone.io/docs/quickstart). You will need these to store and retrieve your vector embeddings of your Evernote notes. 
7. Create an account on [OpenAI](https://platform.openai.com/) and create a secret API key. You will need this to to work with OpenAI embeddings model to vector embeddings and their LLM models.


# Architecture

In recent months, various examples and reference architectures have emerged for using LLM services like OpenAI with the contextual data from your data lakes (e.g.:  Evernote). One such architecture is called retrieval augmented generation (RAG), which combines LLM generative capabilities with the ability to retrieve information from your data lakes using vector databases populated by data in your lake. The RAG architecture looks like the following:
![RAG Architecture](images/RAG-Architecture.png)

This architecture pulls in various architectural components in the AI ecosystem, including foundation language learning models, vector databases, labeling, prompt engineering, etc. As the above diagram illustrates with the dotted boxes, the architecture requires at least two AI data pipelines to be implemented:
- **Document Vector Embedding Ingestion Pipeline** - Collect the documents from your data lake/knowledge base, create a vector embedding, and ingest them into a vector database. 
- **LLM Chat Web Service Endpoint** - Endpoint takes the user request, including current question and chat history, creates a vector embedding, searches for similar documents in the vector database based on the request, and sends the user request and the contextual documents to the LLM to get the next response in the chat conversation.

The below sections outlines how to build these AI pipelines using NIFi.

# Vector Embeddings Ingestion Pipeline 

Document vector embedding pipeline for notes in Evernote is as follows:
![Vector Embeddings Ingestion Pipeline](images/vector-embeddings-ingestion-pipeline.png)

The above flow was implemented with NiFi using the following flow:
![NiFi Flow for Vector Embeddings Ingestion ](images/nifi-flow-embeddings-ingestion.png)

Follow the below instructions to get this flow running:
1. sd
2. 