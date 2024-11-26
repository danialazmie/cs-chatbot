from fastapi import APIRouter, Request
from fastapi.logger import logger
from chatbot.models import Event
from chatbot.bot.chatbot import Chatbot
import requests
import logging
import os

# Business phone number ID
# 481220875069592

router = APIRouter()

conversations = {}

gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers

if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG)

@router.get('/receive')
async def verify_request(request: Request):
    mode = request.query_params['hub.mode']
    challenge = request.query_params['hub.challenge']
    verify_token = request.query_params['hub.verify_token']

    return int(challenge)

@router.post('/receive')
async def receive_event(event: Event):

    received_contacts = False
    received_errors = False
    received_messages = False
    received_statuses = False

    sender_id = None
    message_string = None

    event_header_string = '----------- Received event -----------'

    logger.info('='*len(event_header_string))
    logger.info(event_header_string)
    logger.info('='*len(event_header_string))
    # logger.info(f"Received object:\n```\n{event}\n```\n")
    logger.info(f"Entry size: {len(event.entry)}")
    logger.info(f"Change size: {len(event.entry[0].changes)}")
    # logger.info(f"Value object: {event.entry[0].changes[0].value}")

    value_object = event.entry[0].changes[0].value


    if len(value_object.contacts) > 0:
        event_type = True
    if len(value_object.errors) > 0:
        received_errors = True
    if len(value_object.messages) > 0:
        received_messages = True
    if len(value_object.statuses) > 0:
        received_statuses = True

    if received_messages:
        
        logger.info('Received message')

        sender_id = value_object.messages[0].from_
        message_string = value_object.messages[0].text['body']

        logger.info(f'Sender: {sender_id}')
        logger.info(f'Sent message: {message_string}')

        if sender_id not in conversations.keys():
            conversations[sender_id] = Chatbot()
            logger.info('Created new conversation')
            logger.info(f'{conversations.items()}')
        chatbot = conversations[sender_id]
        response = chatbot.prompt(message_string)
        logger.info(f'Conversation length: {len(chatbot.memory)}')

        ###

        url = "https://graph.facebook.com/v21.0/481220875069592/messages"

        
        token = os.environ['WHATSAPP_TOKEN']


        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": sender_id,
            "type": "text",
            "text": { 
                "preview_url": False,
                "body": response
            }
        }

        resp = requests.post(url, headers=headers, json=body)

        logger.info(f'{resp}')
        ###
    if received_statuses:

        pass

        status = value_object.statuses[0]

        logger.info('Received status')
        logger.info(f'biz_opaque_callback_data = {status.biz_opaque_callback_data}')
        logger.info(f'conversation = {status.conversation}')
        logger.info(f'errors = {status.errors}')
        logger.info(f'id = {status.id}')
        logger.info(f'pricing = {status.pricing}')
        logger.info(f'recipient_id = {status.recipient_id}')
        logger.info(f'status = {status.status}')
        logger.info(f'timestamp = {status.timestamp}')



@router.get('/receive')
async def verify(request: Request):
    mode = request.query_params['hub.mode']
    challenge = request.query_params['hub.challenge']
    verify_token = request.query_params['hub.verify_token']

    return int(challenge)