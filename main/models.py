from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from .utilities import send_activation_notification


# Create your models here.

class AdvUser(AbstractUser):
    """Модель пользователя"""
    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Пользоватль прошел активацию?')
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Отправлять уведомление о новых комментариях')

    class Meta(AbstractUser.Meta):
        """Строковое представление модели"""
        pass


user_registrated = Signal(providing_args=['instance'])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registrated.connect(user_registrated_dispatcher)
