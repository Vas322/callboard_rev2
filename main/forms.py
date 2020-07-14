from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from captcha.fields import CaptchaField

from .models import AdvUser, user_registrated, SuperRubric, SubRubric, AdditionalImage, Bb, Comment


class ChangeUserInfoForm(forms.ModelForm):
    """Форма для занесения данных о пользователе"""
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')


class RegisterUserForm(forms.ModelForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput,
                                help_text='Повторите пароль')

    def clean_password1(self):
        """Очистка пароля1, если не прошел валидацию"""
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        """Проверка пароля1 и пароля2 на идентичность"""
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают',
                                                   code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        """Сохранение введенного пароля. Запрет активации пользователя,
        пока он не подтврдил активацию по почте. Сначала отправляем сигнал, чтобы отправилось
        письмо на эл.почту с кодом"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name',
                  'last_name', 'send_messages')


class SubRubricForm(forms.ModelForm):
    """Форма для завполнения подрубрики"""
    super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(),
                                          empty_label=None, label="Надрубрика", required=True)

    class Meta:
        model = SubRubric
        fields = '__all__'


class SearchForm(forms.Form):
    """Форма поиска"""
    keyword = forms.CharField(required=False, max_length=20, label='Что-то ищете?')


class BbForm(forms.ModelForm):
    """Форма для создания объявления"""

    class Meta:
        model = Bb
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}  # Hiddeninput скрывает значение, т.к. автор заносится автоматом


AIFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')


class UserCommentForm(forms.ModelForm):
    """Форма для создания комментария, авторизованными юзерами"""

    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'bb': forms.HiddenInput}


class GuestCommentForm(forms.ModelForm):
    """Форма для создания комментария гостем"""
    captcha = CaptchaField(label='Введите текст с картинки',
                           error_messages={'invalid': 'Неверный текст'})

    class Meta:
        model = Comment
        exclude = ('is_active',)  # убираем это поле, т.к. активировать может только админ
        widgets = {'bb': forms.HiddenInput}
