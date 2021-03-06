from django.contrib import admin
import datetime

from .forms import SubRubricForm
from .models import AdvUser, SuperRubric, SubRubric, Bb, AdditionalImage, Comment
from .utilities import send_activation_notification


# Register your models here.

def send_activation_notifications(modeladmin, request, queryset):
    """Отправка писем с оповещениями об активации"""
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notifications(rec)
    modeladmin.message_user(request, 'Письма с оповещением отправлены')
    send_activation_notifications.short_description = 'Отправка писем с оповещениями об активации'


class NonActivatedFilter(admin.SimpleListFilter):
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return {
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3-х дней'),
            ('week', 'Не прошли более недели')
        }

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)


class AdvUserAdmin(admin.ModelAdmin):
    """Модель вывода инфы о пользователе в админке"""
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonActivatedFilter,)
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'), ('groups', 'user_permissions'),
              ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)


class SubRubricInline(admin.TabularInline):
    model = SubRubric


class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',)
    inlines = (SubRubricInline,)


class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm


class AdditionalInline(admin.TabularInline):
    """Редактор для работы с дополнительными изображениями"""
    model = AdditionalImage


class BbAdmin(admin.ModelAdmin):
    """Редактор для работы с объявлениями"""
    list_display = ('rubric', 'title', 'content', 'author', 'created_at')
    fields = (('rubric', 'author'), 'title', 'content', 'price', 'contacts',
              'image', 'is_active')
    inlines = (AdditionalInline,)


class CommentAdmin(admin.ModelAdmin):
    """Редактор для работы с комментариями"""
    list_display = ('author', 'content', 'created_at', 'is_active')
    list_display_links = ('author', 'content')
    list_filter = ('is_active',)
    search_fields = ('author', 'content',)
    date_hierarchy = 'created_at'
    fields = ('author', 'content', 'is_active', 'created_at')
    readonly_fields = ('created_at',)


admin.site.register(SubRubric, SubRubricAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(Bb, BbAdmin)
admin.site.register(Comment, CommentAdmin)
