from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .serializer import ImageSerializer


class ImageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Image.objects.filter(user_id=request.user.id)
        if conversations:
            serializer = ImageSerializer(conversations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'No images found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        image = Image(user=user)
        serializer = ImageSerializer(image, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['image'] = serializer.data['image']
            data['success'] = 'Image saved successfully'
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
