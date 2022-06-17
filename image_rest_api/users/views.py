from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView


class ApiOverview(APIView):
    def get(self, request, format=None):
        overview = {
            "users": "/api/users/",
        }
        return Response(overview)
