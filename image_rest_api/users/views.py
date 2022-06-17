from rest_framework.response import Response
from rest_framework.views import APIView


class ApiOverview(APIView):
    def get(self, request, format=None):
        overview = {
            "Show available images": "GET /images/",
            "Upload a new image": "POST /images/",
        }
        return Response(overview)
