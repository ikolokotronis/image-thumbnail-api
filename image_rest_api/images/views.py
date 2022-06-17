import os.path

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .serializer import ImageSerializer
from PIL import Image as PILImage


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
        image_instance = Image(user=user)
        serializer = ImageSerializer(image_instance, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            if user.tier.name == 'Basic':
                original_image_relative_path = 'media/images/' + os.path.basename(image_instance.original_image.path)
                image = PILImage.open(image_instance.original_image.path)
                image.thumbnail((image.width, user.tier.thumbnail_height))
                image.save(original_image_relative_path + '_thumbnail200.png')
                data['thumbnail200'] = "/" + original_image_relative_path + '_thumbnail200.png'
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'Access forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
