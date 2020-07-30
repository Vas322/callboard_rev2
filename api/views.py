from rest_framework.response import Response
from rest_framework.decorators import api_view

from main.models import Bb
from .serializers import BbSerializer


@api_view()
def bbs(request):
    """Список объявлений"""
    if request.method == 'GET':
        bbs = Bb.objects.filter(is_active=True)[:10]
        serializer = BbSerializer(bbs, many=True)
        return Response(serializer.data)
