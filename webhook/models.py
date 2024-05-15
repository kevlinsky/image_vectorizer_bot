from django.db import models

from image_vectorizer_bot.utils import sane_repr


class UserSettings(models.Model):
    tg_id = models.PositiveBigIntegerField(
        verbose_name='Идентификатор пользователя в Telegram',
        unique=True, blank=False, null=False, db_index=True
    )
    radius = models.IntegerField(
        verbose_name='Радиус поиска схожих пикселей',
        blank=True, null=False, default=3
    )
    simplify_tolerance = models.IntegerField(
        verbose_name='Уровень упрощения кривых при построении',
        blank=True, null=False, default=5
    )
    red_threshold = models.IntegerField(
        verbose_name='Пороговое значение для выборки пикселей',
        blank=True, null=False, default=128
    )
    created_at = models.DateTimeField(
        verbose_name='Создан', auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Обновлен', auto_now=True
    )

    class Meta:
        verbose_name = 'Пользовательские настройки'
        verbose_name_plural = 'Список пользовательских настроек'

    __repr__ = sane_repr(
        'tg_id', 'radius', 'simplify_tolerance', 'red_threshold'
    )

    def __str__(self):
        return f'Настройки пользователя {self.tg_id}'
