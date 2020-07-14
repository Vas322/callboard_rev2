from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from .utilities import send_activation_notification, get_timestamp_path, send_new_comment_notification
from django.db.models.signals import post_save


class Rubric(models.Model):
    """Модель рубрики(надрубрики)"""
    name = models.CharField(max_length=20, db_index=True, unique=True,
                            verbose_name='Название рубрики')
    order = models.SmallIntegerField(default=0, verbose_name='Порядок вывода на странице')
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

    def delete(self, *args, **kwargs):
        """Функция удаления юзера"""
        for bb in self.bb_set.all():
            bb.delete()
        super().delete(*args, **kwargs)

    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Пользоватль прошел активацию?')
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Отправлять уведомление о новых комментариях')

    class Meta(AbstractUser.Meta):
        """Строковое представление модели"""
        pass


class Bb(models.Model):
    """Модель объявления"""
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT,
                               verbose_name='Рубрика')
    title = models.CharField(max_length=40, verbose_name='Название товара')
    content = models.TextField(verbose_name='Описание товара')
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path,
                              verbose_name='Изображение товара')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Дата публикации')

    def delete(self, *args, **kwargs):
        """Функция удаления объявления, с предварительным удалением миниатюр,
            связанных с этим объявлением
        """
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        """Строковое представление модели"""
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-created_at']


class AdditionalImage(models.Model):
    """Модель для добавления дополнительных иллюстрация"""
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Дополнительное иллюстрация')

    class Meta:
        verbose_name_plural = 'Дополнительные иллюстрации'
        verbose_name = 'Дополнительная иллюстрация'


class Comment(models.Model):
    """Модель комментария"""
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Публиковать комментарий?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['-created_at']


user_registrated = Signal(providing_args=['instance'])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registrated.connect(user_registrated_dispatcher)



