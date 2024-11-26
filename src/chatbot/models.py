from pydantic import BaseModel, Field
from typing import List
from enum import Enum

# Enumerations

class ConversationTypeEnum(str, Enum):
    
    def __str__(self):
        return str(self.value)
    
    authentication = 'authentication'
    marketing = 'marketing'
    utility = 'utility'
    service = 'service'
    referral_conversation = 'referral_conversation'

class StatusEnum(str, Enum):

    def __str__(self):
        return str(self.value)

    delivered = 'delivered'
    read = 'read'
    sent = 'sent'

class MessageTypeEnum(str, Enum):
    audio = 'audio'
    button = 'button'
    document = 'document'
    text = 'text'
    image = 'image'
    interactive = 'interactive'
    order = 'order'
    sticker = 'sticker'
    system = 'system'
    unknown = 'unknown'
    video = 'video'

class Message(BaseModel):
    id: str
    type: MessageTypeEnum
    from_: str | None = Field(alias='from')
    timestamp: str | int | None = None
    text: dict | None = None
    button: dict | None = None
    context: dict | None = None
    document: dict | None = None
    errors: list | None = []
    identity: dict | None = None
    image: dict | None = None
    interactive: dict | None = None
    order: dict | None = None
    referral: dict | None = None
    sticker: dict | None = None
    system: dict | None = None
    video: dict | None = None


class ConversationType(BaseModel):
    type: ConversationTypeEnum

class Conversation(BaseModel):
    id: str
    origin: ConversationType
    expiration_timestamp: str | None = None

class Status(BaseModel):
    biz_opaque_callback_data: str | None = None
    conversation: Conversation | None = None
    errors: list | None = []
    id: str | None = None
    pricing: dict | None = None
    recipient_id: str | None = None
    status: StatusEnum
    timestamp: int | str

class EventValue(BaseModel):
    messaging_product: str | None = None
    metadata: dict | None = None
    contacts: list = []
    errors: list = []
    messages: List[Message] = []
    statuses: List[Status] = []


class EventChange(BaseModel):
    value: EventValue | None = None
    field: str | None = None


class EventEntry(BaseModel):
    id: str | None = None
    changes: List[EventChange] | None = None


class Event(BaseModel):
    object: str | None = None
    entry: List[EventEntry] | None = []

