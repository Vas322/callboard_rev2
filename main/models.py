from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from .utilities import send_activation_notification


# Create your models here.
class Rubric(models.Model):
    """Модель рубрики(надрубрики)"""
    name = models.CharField(max_length=20, db_index=True, unique=True,
                            verbose_name='Название рубрики')
    order = models.SmallIntegerField(default=0, verbose_name='Порядок')
    super_rubric = models.ForeignKey('Superrubric', on_delete=models.PROTECT, null=True,
                                     blank=True, verbose_name='Надрубрика')


class SuperRubricManager(models.Manager):
    """Диспетчер записей"""

    def get_queryset(self):
        """Переопределяем условия фильтрации. Выбираем только записи
        с пустым полем super_rubric, т.е. надрубрики
        """
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    """Модель суперрубрики"""
    objects = SuperRubricManager()

    def __str__(self):
        """Строковое представление названия"""
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')  # сортировка записей - сначала возростание порядка, потом название
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'


class SubRubricManager(models.Manager):
    """Диспетчер записей"""

    def get_queryset(self):
        """Переопределяем условия фильтрации. Выбираем только записи
        с не пустыми полем super_rubric т.е. подрубрики
        """
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    """Модель подрубрики"""
    objects = SubRubricManager()

    def __str__(self):
        """Строковое представление отношения надрубрики к подрубрике
        """
        return '%s - %s' % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'


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
