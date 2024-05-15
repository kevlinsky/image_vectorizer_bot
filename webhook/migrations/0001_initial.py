# Generated by Django 5.0.6 on 2024-05-14 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_id', models.PositiveBigIntegerField(db_index=True, unique=True, verbose_name='Идентификатор пользователя в Telegram')),
                ('radius', models.IntegerField(blank=True, default=3, verbose_name='Радиус поиска схожих пикселей')),
                ('simplify_tolerance', models.IntegerField(blank=True, default=5, verbose_name='Уровень упрощения кривых при построении')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
            ],
            options={
                'verbose_name': 'Пользовательские настройки',
                'verbose_name_plural': 'Список пользовательских настроек',
            },
        ),
    ]