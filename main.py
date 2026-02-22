import logging
from fastapi import FastAPI, HTTPException
from schemas import TranslateRequest, TranslateResponse, TelegramUpdate, TelegramMessage, TelegramChat
from llm_client import call_openrouter
from telegram_client import send_message

# Configure logging (no secrets in format)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """Translate text using OpenRouter LLM."""
    try:
        result = call_openrouter(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        return TranslateResponse(translation=result)
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Translation service failed")


@app.post("/tg/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Handle incoming Telegram webhook updates."""
    try:
        # Extract message and chat info
        if not update.message:
            logger.warning("Webhook received without message")
            return {"ok": True}
        
        message = update.message
        if not message.text or not message.chat:
            logger.warning("Message missing text or chat info")
            return {"ok": True}
        
        user_text = message.text
        chat_id = message.chat.id
        
        logger.info(f"Received message from chat {chat_id}: {user_text}")
        
        # Translate to Russian
        try:
            translation = call_openrouter(
                text=user_text,
                source_lang="auto",
                target_lang="ru"
            )
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            translation = "Извините, произошла ошибка при переводе."
        
        # Send translation back to user
        try:
            send_message(chat_id=chat_id, text=translation)
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
        
        return {"ok": True}
    
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return {"ok": True}
