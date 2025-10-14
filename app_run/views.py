from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AthleteInfo, Challenge, Run, User
from .serializers import ChallengeSerializer, RunSerializer, UserSerializer


# Добавляем свойство для подсчета завершенных забегов
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
    Запуск забега
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
    def post(self, request, run_id):
        run = get_object_or_404(Run, pk=run_id)
        if run.status == "in_progress":
            run.status = "finished"
            run.save()

            user = run.athlete
            runs_finished_count = user.runs_finished

            if runs_finished_count >= 10:
                try:
                    # Используем get_or_create для предотвращения дублирования
                    challenge, created = Challenge.objects.get_or_create(
                        athlete=user, full_name="Сделай 10 забегов!"
                    )
                except IntegrityError:
                    return Response(
                        {"error": "Ошибка создания челленджа"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            return Response({"status": "finished"}, status=status.HTTP_200_OK)

        elif run.status == "init":
            return Response(
                {"status": "not started"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"status": "already finished"}, status=status.HTTP_400_BAD_REQUEST
            )


class GetChallenges(APIView):
    def get(self, request):
        athlete_id = request.GET.get("athlete")

        try:
            if athlete_id:
                challenges = Challenge.objects.filter(athlete_id=athlete_id)
            else:
                challenges = Challenge.objects.all()

            response_data = [
                {"full_name": challenge.full_name, "athlete": challenge.athlete.id}
                for challenge in challenges
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
    Работа с информацией об атлете
    """

    def get(self, request, id):
        user = get_object_or_404(User, pk=id)
        athlete, _ = AthleteInfo.objects.get_or_create(user=user)
        response_data = {
            "user_id": user.pk,
            "goals": athlete.goals,
            "weight": athlete.weight,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, id):
        user = get_object_or_404(User, pk=id)
        weight = request.data.get("weight")
        goals = request.data.get("goals")

        if weight is not None:
            try:
                weight_value = float(weight)
            except ValueError:
                return Response(
                    "Вес должен быть числовым значением",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not 0 < weight_value < 900:
                return Response(
                    "Некорректное значение веса", status=status.HTTP_400_BAD_REQUEST
                )
        else:
            weight_value = None

        update_fields = {}
        if weight_value is not None:
            update_fields["weight"] = weight_value
        if goals is not None:
            update_fields["goals"] = goals

        athlete, created = AthleteInfo.objects.update_or_create(
            user=user, defaults=update_fields
        )
        return Response(
            {"weight": athlete.weight, "goals": athlete.goals},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
