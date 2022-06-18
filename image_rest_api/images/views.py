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
            original_image_absolute_path = image_instance.original_image.path
            original_image_relative_path = image_instance.original_image.url
            file_name, file_extension = os.path.splitext(original_image_relative_path)
            with PILImage.open(original_image_absolute_path) as image:
                if user.tier.name == "Basic":
                    image.thumbnail((image.width, 200))
                    image.save("." + file_name + "_200px_thumbnail" + file_extension)
                    data['200px_thumbnail'] = file_name + "_200px_thumbnail" + file_extension
                    data["success"] = "Image uploaded successfully"
                    return Response(data, status=status.HTTP_200_OK)
                elif user.tier.name == "Premium":
                    image.thumbnail((image.width, 400))
                    image.save("." + file_name + "_400px_thumbnail" + file_extension)
                    data['400px_thumbnail'] = file_name + "_400px_thumbnail" + file_extension
                    image.thumbnail((image.width, 200))
                    image.save("." + file_name + "_200px_thumbnail" + file_extension)
                    data['200px_thumbnail'] = file_name + "_200px_thumbnail" + file_extension
                    data["original_image"] = image_instance.original_image.url
                    data["success"] = "Image uploaded successfully"
                    return Response(data, status=status.HTTP_200_OK)
                elif user.tier.name == "Enterprise":
                    image.thumbnail((image.width, 400))
                    image.save("." + file_name + "_400px_thumbnail" + file_extension)
                    data['400px_thumbnail'] = file_name + "_400px_thumbnail" + file_extension
                    image.thumbnail((image.width, 200))
                    image.save("." + file_name + "_200px_thumbnail" + file_extension)
                    data['200px_thumbnail'] = file_name + "_200px_thumbnail" + file_extension
                    data["original_image"] = image_instance.original_image.url
                    data["expiring_link"] = ""  # todo: implement expiring link
                    data["success"] = "Image uploaded successfully"
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    image.thumbnail((image.width, user.tier.thumbnail_height))
                    image.save("." + file_name + "_" + str(user.tier.thumbnail_height) + "px_thumbnail" + file_extension)
                    data[str(user.tier.thumbnail_height) + 'px_thumbnail'] = file_name + \
                                                                             "_" + \
                                                                             str(user.tier.thumbnail_height) + \
                                                                             "px_thumbnail" + \
                                                                             file_extension
                    if user.tier.presence_of_original_file_link:
                        data["original_image"] = image_instance.original_image.url
                    if user.tier.ability_to_fetch_expiring_link:
                        pass  # todo: implement expiring link
                    data["success"] = "Image uploaded successfully"
                    return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
