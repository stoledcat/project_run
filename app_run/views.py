from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import Run
from .serializers import RunSerializer, UserSerializer


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
    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer

    def start_run(self, request, pk=None):
        run_id = Run.objects.get("id")
        status_run = Run.objects.get("status")
        run = get_list_or_404(Run, id=run_id)
        if status_run != "init":
            return Response(status=status.HTTP_400)



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        qs = self.queryset
        qs = qs.filter(is_superuser=False)

        is_staff = self.request.query_params.get("type")

        if is_staff == "coach":
            qs = qs.filter(is_staff=True)
        elif is_staff == "athlete":
            qs = qs.filter(is_staff=False)
        else:
            pass
        return qs
