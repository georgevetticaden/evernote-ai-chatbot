# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import uuid

from nifiapi.properties import PropertyDescriptor
from nifiapi.properties import StandardValidators
from nifiapi.properties import ExpressionLanguageScope
from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult


import pinecone

class PutPineconeVectorEmbedding(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']
    class ProcessorDetails:
        dependencies = ['langchain', 'openai', 'pinecone-client','tiktoken']
        version = '0.0.1-SNAPSHOT'
        description = 'Upserts vector text embeddings into Pinecone with the configured index. Expected format is a list of json elements with text, embeddign and metadata'
        tags = [ 'Pinecone', 'AI, ''OpenAI',  'Vector Database', 'Embeddings' ]


    def __init__(self, **kwargs):
        # Build Property Descriptors


        self.pinecone_api_key = PropertyDescriptor(
            name="Pinecone API Key",
            description="The API key to connect to the Pinecone",
            required = True,
            sensitive = True
        )
        self.pinecone_environment_name = PropertyDescriptor(
            name="Pinecone Env Name",
            description="The environment that the Pinecone index is located.",
            required = True,
            sensitive = True
        )

        self.pinecone_index_name = PropertyDescriptor(
            name="Index Name",
            description="The Pinecone index to store the embeddings.",
            required = True,
        )

        self.pinecone_namespace = PropertyDescriptor(
            name="Namepace",
            description="The  namespace within the index to store the vector embeddings.",
            required = True,
        )

        self.batch_size = PropertyDescriptor(
            name="Batch Size",
            default_value = "100",
            description="The number of text docs to batch up before upserting into Pinecone",
            required=True,
        )

        self.descriptors = [self.pinecone_api_key, self.pinecone_environment_name, self.pinecone_index_name, self.pinecone_namespace, self.batch_size]
        # self.descriptors = [self.vector_embedding_model_service]

    def onScheduled(self, context):
        self.logger.info("Initializing Pinecone Index")

        # INitialize Pinecone and get the indecx we will be upserting into. Assume the index already exists
        pinecone_api_key =  context.getProperty(self.pinecone_api_key.name).getValue()
        pinecone_environment = context.getProperty(self.pinecone_environment_name.name).getValue()
        pinecone_index = context.getProperty(self.pinecone_index_name.name).getValue()


        pinecone.init(
            api_key=pinecone_api_key,
            environment=pinecone_environment
        )
        self.pinecone_index = pinecone.Index(index_name=pinecone_index)



    def transform(self, context, flowFile):
        self.logger.info("Inside transform of PutPineconeVectorEmbedding..")

        # Convert the json embedding string into list of text embedding documents that contain text, embedding and metadata for each text chunk
        chunked_docs_string = flowFile.getContentsAsBytes().decode('utf-8')
        chunk_docs_json_list_deserialized = json.loads(chunked_docs_string)

        # Store the text, embedding and metadata in seperate lists which we will use to batch up and insert into pinecone
        texts = []
        embeddings = []
        metadatas = []
        for doc_dict in chunk_docs_json_list_deserialized:
            texts.append(doc_dict["text"])
            embeddings.append(doc_dict['embedding'])
            metadatas.append(doc_dict['metadata'])


        batch_size = context.getProperty(self.batch_size.name).asInteger()
        namespace = context.getProperty(self.pinecone_namespace.name).getValue()

        # Create the List of tuples to insert into pinecone where tuple is string Id, tuple 2 is list of floats, and tuple 3 is metadata dictionary
        vector_ids = []
        for i in range(0, len(texts), batch_size):
            # set end position of batch
            i_end = min(i + batch_size, len(texts))
            # get batch of texts and ids
            lines_batch = texts[i:i_end]
            # create ids
            ids_batch = [str(uuid.uuid4()) for n in range(i, i_end)]
            vector_ids.extend(ids_batch)
            # get batch of embeddings
            embeddings_batch = embeddings[i:i_end]
            # prep metadata and upsert batch
            metadata_batch = metadatas[i:i_end]

            for j, line in enumerate(lines_batch):
                metadata_batch[j]["text"] = line
            to_upsert = zip(ids_batch, embeddings_batch, metadata_batch)

            # upsert to Pinecone
            self.pinecone_index.upsert(vectors=list(to_upsert), namespace=namespace)

        # Return a list of Ids for each embedding inserted
        vector_ids_json_string = json.dumps(vector_ids)
        self.logger.info(str(len(vector_ids)) + " vectors were inserted wtih the following ids: " + vector_ids_json_string)

        return FlowFileTransformResult(relationship="success", contents=vector_ids_json_string)


    def getPropertyDescriptors(self):
        return self.descriptors
