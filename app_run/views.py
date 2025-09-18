from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.conf import settings
from .models import Run
from .serializers import RunSerializer


# Create your views here.
@api_view(["GET"])
def company_details(request):
    details = {
        "company_name": settings.COMPANY_NAME,
        "slogan": settings.SLOGAN,
        "contacts": settings.CONTACTS,
    }

    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
