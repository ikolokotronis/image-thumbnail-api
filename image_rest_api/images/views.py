import os.path

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .serializer import ImageSerializer
from PIL import Image as PILImage


class ApiOverview(APIView):
    def get(self, request, format=None):
        overview = {
            "Show available images": "GET /images/",
            "Upload a new image": "POST /images/",
        }
        return Response(overview)


class ImageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        images = Image.objects.filter(user_id=request.user.id)
        if images:
            serializer = ImageSerializer(images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'No images found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        image_instance = Image(user=user)
        serializer = ImageSerializer(image_instance, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            if user.tier.name == "Basic":
                original_image_absolute_path = image_instance.original_image.path
                image = PILImage.open(original_image_absolute_path)
                image.thumbnail((image.width, 200))
                image.save("media/images/thumbnail_200px_" + os.path.basename(image_instance.original_image.path))
                data['thumbnail_200px'] = "/"+"media/images/thumbnail_200px_" \
                                          + os.path.basename(image_instance.original_image.path)
                data["success"] = "Image uploaded successfully"
                return Response(data, status=status.HTTP_200_OK)
            elif user.tier.name == "Premium":
                pass
            elif user.tier.name == "Enterprise":
                pass
            else:
                original_image_absolute_path = image_instance.original_image.path
                image = PILImage.open(original_image_absolute_path)
                image.thumbnail((image.width, user.tier.thumbnail_height))
                image.save("media/images/thumbnail_"+str(user.tier.thumbnail_height)+"px_"+
                           os.path.basename(image_instance.original_image.path))
                data['thumbnail_'+str(user.tier.thumbnail_height)+'px'] = "/" + "media/images/thumbnail_"\
                                                                          + str(user.tier.thumbnail_height)+"px_" + \
                                                                          os.path.basename(image_instance.original_image.path)
                data["success"] = "Image uploaded successfully"
                return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
