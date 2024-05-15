import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from webhook.models import UserSettings
from webhook.tasks import vectorize_image


class TelegramWebhook(APIView):
    def __init__(self, *args, **kwargs):
        self.reply_url = (
            'https://api.telegram.org'
            f'/bot{settings.TELEGRAM_API_TOKEN}'
            '/sendMessage'
        )
        self.commands_mapper = {
            'settings': self.process_settings_command,
            'start': self.process_start_command,
            'radius': self.process_set_settings_command,
            'simplify_tolerance': self.process_set_settings_command,
            'red_threshold': self.process_set_settings_command,
        }
        super().__init__(*args, **kwargs)

    def process_start_command(self, message, *args, **kwargs):
        tg_id = message['message']['from']['id']
        name = message['message']['from']['first_name']
        chat_id = message['message']['chat']['id']

        UserSettings.objects.update_or_create(tg_id=tg_id)

        reply = (
            f"Hi, {name}!\n"
            "You\'re using bot for vectorizing images.\n\n"
            "Possible commands:\n"
            "/start - start the bot\n"
            "/settings - print current bot settings\n"
            "/radius - set the radius setting\n"
            "/simplify_tolerance - set the simplify_tolerance setting\n"
            "/red_threshold - set the red_threshold setting"
        )

        data = {'chat_id': chat_id, 'text': reply}

        requests.post(self.reply_url, data=data)

    def process_settings_command(self, message, *args, **kwargs):
        tg_id = message['message']['from']['id']
        chat_id = message['message']['chat']['id']

        user_settings = UserSettings.objects.get(tg_id=tg_id)

        reply = (
            "Your bot settings provided below:\n\n"
            f"*radius* = {user_settings.radius}\n"
            f"*simplify_tolerance* = {user_settings.simplify_tolerance}\n"
            f"*red_threshold* = {user_settings.red_threshold}"
        )

        data = {'chat_id': chat_id, 'text': reply, 'parse_mode': 'markdown'}

        requests.post(self.reply_url, data=data)

    def process_set_settings_command(self, message, *args, **kwargs):
        tg_id = message['message']['from']['id']
        chat_id = message['message']['chat']['id']
        command_name = kwargs.pop('command_name')
        edge_values = {
            'radius': (1, 10),
            'simplify_tolerance': (1, 10),
            'red_threshold': (1, 255),
        }

        if len(args) != 1:
            reply = f'Wrong number of arguments: *{len(args)}*'
            data = {
                'chat_id': chat_id,
                'text': reply,
                'parse_mode': 'markdown'
            }
            requests.post(self.reply_url, data=data)
            return

        try:
            value = int(args[0])
            ev = edge_values.get(command_name, (1, 10))

            if not (ev[0] <= value <= ev[1]):
                reply = (
                    f'*{command_name}* value should be '
                    f'between {ev[0]} and {ev[1]}'
                )
                data = {
                    'chat_id': chat_id,
                    'text': reply,
                    'parse_mode': 'markdown'
                }
                requests.post(self.reply_url, data=data)
                return

            user_settings = UserSettings.objects.get(tg_id=tg_id)
            setattr(user_settings, command_name, value)
            user_settings.save()

            reply = f'*{command_name}* setting set to *{value}*'
        except Exception:
            reply = (
                f'"{args[0]}" is not a correct '
                f'value for *{command_name}* setting'
            )

        data = {'chat_id': chat_id, 'text': reply, 'parse_mode': 'markdown'}

        requests.post(self.reply_url, data=data)

    def process_telegram_message(self, message, *args, **kwargs):
        chat_id = message['message']['chat']['id']
        data = {'chat_id': chat_id, 'text': 'Command not found'}
        requests.post(self.reply_url, data=data)

    def process_file_message(self, message, *args, **kwargs):
        chat_id = message['message']['chat']['id']
        mime_type = message['message']['document']['mime_type']

        if not mime_type.startswith('image'):
            reply = 'Wrong type of file. Skipped'
            data = {'chat_id': chat_id, 'text': reply}
            requests.post(self.reply_url, data=data)
            return

        vectorize_image.s(message).apply_async(
            time_limit=settings.VECTORIZE_IMAGE_TIME_LIMIT,
            soft_time_limit=settings.VECTORIZE_IMAGE_SOFT_TIME_LIMIT,
        )
        reply = (
            'Image downloaded and started to vectorize.\n'
            'You\'ll receive a message with the result '
            '.zip archive in 5-10 minutes'
        )
        data = {'chat_id': chat_id, 'text': reply}
        requests.post(self.reply_url, data=data)

    def post(self, request):
        key = 'message' if 'message' in request.data else 'edited_message'
        message = request.data.pop(key)
        request.data['message'] = message

        if 'text' in request.data['message']:
            args = request.data['message']['text'].split(' ')
            command_name = args.pop(0).replace('/', '')
            method = self.commands_mapper.get(
                command_name, self.process_telegram_message
            )
        elif 'document' in request.data['message']:
            method = self.process_file_message
            args = ()
            command_name = ''
        else:
            method = self.process_telegram_message
            args = ()
            command_name = ''

        method(request.data, *args, command_name=command_name)

        return Response({'success': True})
