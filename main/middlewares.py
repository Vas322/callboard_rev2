from .models import SubRubric


def bboard_context_processor(request):
    """Обработчик контекста для вывода подрубрик"""
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    return context
