import logging
import os
import requests
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = '7512683045:AAG4lcODliCYSLIVC6BxFrat19vKJzSDpHk'
BACKEND_URL = 'http://localhost:8000'
IMAGE_ENDPOINT = '/api/image/detect'
VIDEO_ENDPOINT = '/api/video/detect_video'
TEMP_DIR = 'tmp'
os.makedirs(TEMP_DIR, exist_ok=True)

async def download_file(file_id: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    new_file = await context.bot.get_file(file_id)
    file_path = os.path.join(TEMP_DIR, new_file.file_path.split('/')[-1])
    await new_file.download_to_drive(file_path)
    logger.info(f"Downloaded file to {file_path}")
    return file_path

def send_to_backend(file_path: str, endpoint: str, media_type: str) -> str:
    url = BACKEND_URL + endpoint
    files = {}
    if media_type == 'image':
        files = {'file': open(file_path, 'rb')}
    elif media_type == 'video':
        files = {'video': open(file_path, 'rb')}
    else:
        raise ValueError("Unsupported media type")

    logger.info(f"Sending file {file_path} to backend at {url}")
    response = requests.post(url, files=files)

    files['file'].close() if media_type == 'image' else files['video'].close()

    if response.status_code != 200:
        logger.error(f"Backend returned status code {response.status_code}")
        raise Exception(f"Backend error: {response.text}")

    processed_file_path = os.path.join(TEMP_DIR, f"processed_{os.path.basename(file_path)}")
    with open(processed_file_path, 'wb') as f:
        f.write(response.content)
    logger.info(f"Received processed file at {processed_file_path}")
    return processed_file_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте, я помощник сервиса MoleScane! Отправьте мне фотографию или видео интересующей области кожи, чтобы я проанализировал её :)"
    )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        user = update.message.from_user.username or update.message.from_user.first_name
        logger.info(f"Received image from {user}")

        image_path = await download_file(file_id, context)
        processed_image_path = send_to_backend(image_path, IMAGE_ENDPOINT, 'image')

        with open(processed_image_path, 'rb') as f:
            await update.message.reply_photo(photo=InputFile(f))

        os.remove(image_path)
        os.remove(processed_image_path)
        logger.info("Processed image sent and temporary files removed.")

    except Exception as e:
        logger.error(f"Error handling image: {e}")
        await update.message.reply_text("Извините, произошла ошибка при обработке файла :(")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming videos."""
    try:
        video = update.message.video
        if not video:
            await update.message.reply_text("No video found in the message.")
            return

        file_id = video.file_id
        user = update.message.from_user.username or update.message.from_user.first_name
        logger.info(f"Received video from {user}")

        video_path = await download_file(file_id, context)
        processed_video_path = send_to_backend(video_path, VIDEO_ENDPOINT, 'video')

        with open(processed_video_path, 'rb') as f:
            await update.message.reply_video(video=InputFile(f))

        os.remove(video_path)
        os.remove(processed_video_path)
        logger.info("Processed video sent and temporary files removed.")

    except Exception as e:
        logger.error(f"Error handling video: {e}")
        await update.message.reply_text("Sorry, there was an error processing your video.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await None

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Bot is starting...")
    application.run_polling()