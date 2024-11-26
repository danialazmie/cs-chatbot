from .utils import load_credentials
from .prompts import *
# from .tool import Tool, change_email, change_email_params, change_phone, change_phone_params


import logging
import json
import streamlit as st
from fastapi.logger import logger
import uuid

from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import AzureOpenAIChatGenerator
from haystack_integrations.components.generators.google_vertex import VertexAIGeminiChatGenerator
# from haystack.components.embedders import AzureOpenAITextEmbedder
from haystack.components.embedders import OpenAITextEmbedder
from haystack_integrations.components.retrievers.pinecone import PineconeEmbeddingRetriever
from haystack_integrations.document_stores.pinecone import PineconeDocumentStore

# gunicorn_logger = logging.getLogger('gunicorn.error')
# logger.handlers = gunicorn_logger.handlers

# if __name__ != "main":
#     logger.setLevel(gunicorn_logger.level)
# else:
#     logger.setLevel(logging.DEBUG)


class Chatbot:

    def __init__(
        self, 
        model: str = 'OpenAI',
        tools: list = [],
    ):

        """
        Constructor for Chatbot class. A single instance represents as a single conversation

        Args:
            model (str): Model to use for chat generation ('OpenAI' or 'Gemini'). Defaults to 'OpenAI'.
            tools (list): List of tools available for Function Calling. Defaults to an empty list.

        Raises:
            ValueError: If model is not supported.

        """
        load_credentials('credentials.yaml')

        if logging.getLogger(st.__name__).hasHandlers():
            self.logger = logging.getLogger(st.__name__)
            self.logger.setLevel(self.logger.level)

        elif logging.getLogger('gunicorn.error').hasHandlers():
            self.logger = logging.getLogger('gunicorn.error')
            self.logger.setLevel(self.logger.level)

        elif logging.getLogger(__name__).hasHandlers():
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(self.logger.level)

        else:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))

            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(handler)

        generation_kwargs = {}

        if len(tools) > 0:
            generation_kwargs['tools'] = [tool.tool_dict for tool in tools]

        if model == 'OpenAI':
            self.chat_generator = AzureOpenAIChatGenerator(
                azure_endpoint='https://rev-chatgpt-openai.openai.azure.com/',
                azure_deployment='gpt-4o-mini',
                generation_kwargs=generation_kwargs
            )

        elif model == 'Gemini':
            self.chat_generator = VertexAIGeminiChatGenerator(
                model='gemini-1.5-flash-002',
                project_id='mp-bigdata'
            )

        else:
            raise ValueError(f"Model {model} not supported")

        self.id = uuid.uuid4().hex
        self.memory = [ChatMessage.from_system(QA_SYSTEM_PROMPT)]
        self.tools = {tool.name: tool for tool in tools}
        self.document_store = PineconeDocumentStore(index="tonton-faq", dimension=1536)

        self.query_pipeline = Pipeline()
        self.query_pipeline.add_component("text_embedder", OpenAITextEmbedder())
        self.query_pipeline.add_component("retriever", PineconeEmbeddingRetriever(document_store=self.document_store, top_k=5))
        self.query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

    def prompt(self, message):

        """
        Handles a user message and responds accordingly.

        Retrieves relevant documents from the knowledge base based on the user's message.
        Then uses the chat generator to generate a response based on the user's message and the retrieved documents.
        If the generated response is a function call, it calls the tool function and appends the result to the chat memory.
        Finally it returns the response as a string.

        Args:
            message (str): The user's message.

        Returns:
            str: The AI's response.
        """

        self.logger.info(f'USER: {message}')

        documents = self.query_pipeline.run({"text_embedder":{"text": message}})
        documents = documents['retriever']['documents']
        documents_str = '\n'.join([doc.content for doc in documents])

        self.logger.info('RETRIEVER: ' + ', '.join([doc.id for doc in documents]))

        self.memory.append(ChatMessage.from_user(QA_USER_PROMPT.format(documents=documents_str, question=message)))
        response = self.chat_generator.run(self.memory)
        response = response['replies'][0]
        response_str = response.content
        self.memory.append(response)

        if 'finish_reason' in response.meta.keys():
            if response.meta['finish_reason'] == 'tool_calls':
                response = self.call_function(json.loads(response.content)[0])
                self.memory.append(response)
                response_str = response.content

        self.logger.info(f'AI: {response_str}')
        return response_str
    
    def call_function(self, function_call: dict):

        """
        Calls a tool function and appends the result to the chat memory.

        Args:
            function_call (dict): A dictionary containing the name of the function and its arguments.

        Returns:
            A ChatMessage object containing the result of the function call.
        """
        
        function = function_call['function']
        args = function['arguments']
        name = function['name']

        self.logger.debug(f'ACTION: INPUT {name}({args})')
        
        func_result = self.tools[name](**json.loads(args))

        self.logger.debug(f'ACTION: OUTPUT {func_result}')

        self.memory.append(ChatMessage.from_function(str(func_result), name))
        response = self.chat_generator.run(self.memory)
        response = response['replies'][0]

        return response
