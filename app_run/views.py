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

from .models import AthleteInfo, Run
from .serializers import RunSerializer, UserSerializer


# Create your views here.
@property
def runs_finished(self):
    return self.run_set.filter(status="finished").count()


User.add_to_class("runs_finished", runs_finished)


@api_view(["GET"])
def company_details(request):
    details = {
        "company_name": settings.COMPANY_NAME,
        "slogan": settings.SLOGAN,
        "contacts": settings.CONTACTS,
    }

    return Response(details)


class RunPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "size"


class UserPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "size"


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "athlete", "created_at"]
    ordering_fields = ["created_at"]
    ordering = ["id"]

    def paginate_queryset(self, queryset):
        if "size" in self.request.query_params:
            return super().paginate_queryset(queryset)

    pagination_class = RunPagination


class RunStartAPIView(APIView):
    """
    Класс для запуска забега
    """

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
    """
    Класс для остановки забега
    """

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


class GetOrCreateAthleteInfo(APIView):
    """
    Класс для получения или добавления информации об атлете
    """

    def get(self, request, id):
        user = get_object_or_404(User, pk=id)

        weight = request.query_params.get("weight")
        goals = request.query_params.get("goals")

        if weight is None:
            return Response("Wrong weight: None", status=status.HTTP_400_BAD_REQUEST)

        try:
            weight_value = int(weight)
        except ValueError:
            return Response("Значение веса должно быть числом", status=status.HTTP_400_BAD_REQUEST)
        
        if weight_value < 0 or weight_value > 900:
            return Response("Неверное значение веса", status=status.HTTP_400_BAD_REQUEST)

        athlete, created = AthleteInfo.objects.get_or_create(user=user, defaults={"weight": weight, "goals": goals})
        return Response({"weight": athlete.weight, "goals": athlete.goals, "created": created})

    def put(self, request, id):
        user = get_object_or_404(User, pk=id)

        weight = request.query_params.get("weight")
        goals = request.query_params.get("goals")

        if weight is None:
            return Response("Wrong weight: None", status=status.HTTP_400_BAD_REQUEST)

        try:
            weight_value = int(weight)
        except ValueError:
            return Response("Значение веса должно быть числом", status=status.HTTP_400_BAD_REQUEST)
        
        if weight_value < 0 or weight_value > 900:
            return Response("Неверное значение веса", status=status.HTTP_400_BAD_REQUEST)

        athlete, created = AthleteInfo.objects.update_or_create(user=user, defaults={"weight": weight, "goals": goals})
        return Response({"weight": athlete.weight, "goals": athlete.goals, "created": created})