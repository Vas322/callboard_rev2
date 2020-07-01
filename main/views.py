from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


def other_page(request, page):
    """Контроллер выводит инфу о сайте"""
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


# Create your views here.
def index(request):
    """контроллер главной страницы"""
    return render(request, 'main/index.html')


class BBLoginView(LoginView):
    """Контроллер для авторизации пользователя"""
    template_name = 'main/login.html'


class BBLogoutView(LoginRequiredMixin, LogoutView):
    """Контроллер выхода из профиля"""
    template_name = 'main/logout.html'


@login_required
def profile(request):
    """Контроллер профиля пользователя"""
    return render(request, 'main/profile.html')
