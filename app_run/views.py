from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

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


class RunPagination(PageNumberPagination):
    page_size = 1
    page_query_param = "page"
    page_size_query_param = "size"
    max_page_size = 3


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "athlete", "created_at"]
    ordering_fields = ["created_at"]
    ordering = ["id"]
    pagination_class = RunPagination


class RunStartAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, pk=run_id)

        if run.status == "init":
            run.status = "in_progress"
            run.save()
            return Response({"status": "in_progress"}, status=status.HTTP_200_OK)
        elif run.status == "in_progress":
            return Response(
                {"status": "already in progress"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"status": "already finished"}, status=status.HTTP_400_BAD_REQUEST
            )


class RunStopAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, pk=run_id)

        if run.status == "in_progress":
            run.status = "finished"
            run.save()
            return Response({"status": "finished"}, status=status.HTTP_200_OK)
        elif run.status == "init":
            return Response(
                {"status": "not started"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"status": "already finished"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserPagination(PageNumberPagination):
    page_size = 1
    page_query_param = "page"
    page_size_query_param = "size"
    max_page_size = 3


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["date_joined"]
    
    def paginate_queryset(self, queryset):
        if "size" in self.request.query_params:
            return super().paginate_queryset(queryset)
    
    pagination_class = UserPagination

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
