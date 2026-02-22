from pydantic import BaseModel
from typing import Optional


class TranslateRequest(BaseModel):
    text: str
    target_lang: str


class TranslateResponse(BaseModel):
    detected_lang: str
    normalized_text: str
    translated_text: str


class TelegramChat(BaseModel):
    id: int
    type: str


class TelegramUser(BaseModel):
    id: int
    is_bot: bool = False
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class TelegramMessage(BaseModel):
    message_id: int
    from_: Optional[TelegramUser] = None
    chat: TelegramChat
    text: Optional[str] = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
