import requests
from django.conf import settings
from django.utils import timezone

from image_vectorizer_bot.celery import app
from vectorizer.utils import image_to_svg
from webhook.models import UserSettings
from logging import getLogger


task_logger = getLogger(__name__)
FILE_URL = f'https://api.telegram.org/bot{settings.TELEGRAM_API_TOKEN}/getFile'
DOWNLOAD_URL = (
    f'https://api.telegram.org/file/bot{settings.TELEGRAM_API_TOKEN}/'
)
SEND_URL = (
    f'https://api.telegram.org/bot{settings.TELEGRAM_API_TOKEN}/sendDocument'
)


@app.task
def vectorize_image(message):
    file_id = message['message']['document']['file_id']

    response = requests.get(FILE_URL, data={'file_id': file_id})
    file_path = response.json().get('result', {}).get('file_path')
    response = requests.get(f'{DOWNLOAD_URL}/{file_path}')
    file_bytes = response.content

    tg_id = message['message']['from']['id']
    user_settings = UserSettings.objects.get(tg_id=tg_id)

    zip_bytes = image_to_svg(
        file_bytes, user_settings.radius,
        user_settings.simplify_tolerance, user_settings.red_threshold
    )

    chat_id = message['message']['chat']['id']
    file_name = timezone.now().strftime('%d-%m-%Y_%H_%M_%S')
    response = requests.post(
        SEND_URL,
        data={'chat_id': chat_id},
        files={'document': (f'archive_{file_name}.zip', zip_bytes)}
    )
    return response.status_code == 200
