from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
@api_view(["GET"])
def get_about(request):
    company_name = "5 ростовских вёрст"
    slogan = "Суббота, утро, парк"
    contacts = "г. Ростов-на-Дону, ул. Береговая 10"

    return Response(
        {"company_name": company_name, "slogan": slogan, "contacts": contacts}
    )
