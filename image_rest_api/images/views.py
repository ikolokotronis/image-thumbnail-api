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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = {'Basic': self.__basic_processing,
                        'Premium': self.__premium_processing,
                        'Enterprise': self.__enterprise_processing}

    def __file_processing(self, image, image_instance, size):
        image_relative_path = image_instance.original_image.url
        file_name, file_extension = os.path.splitext(image_relative_path)
        image.thumbnail((image.width, size))
        return file_name, file_extension

    def __basic_processing(self, image_instance, image, *args):
        file_name, file_extension = self.__file_processing(image, image_instance, 200)
        image.save(f".{file_name}_200px_thumbnail{file_extension}")
        data = {'200px_thumbnail': f'{file_name}_200px_thumbnail{file_extension}',
                'success': 'Image uploaded successfully'}
        return Response(data, status=status.HTTP_201_CREATED)

    def __premium_processing(self, image_instance, image, *args):
        file_name, file_extension = self.__file_processing(image, image_instance, 400)
        image.save(f".{file_name}_400px_thumbnail{file_extension}")
        file_name, file_extension = self.__file_processing(image, image_instance, 200)
        image.save(f".{file_name}_200px_thumbnail{file_extension}")
        data = {'400px_thumbnail': f'{file_name}_400px_thumbnail{file_extension}',
                '200px_thumbnail': f'{file_name}_200px_thumbnail{file_extension}',
                'original_image': image_instance.original_image.url,
                'success': 'Image uploaded successfully'}
        return Response(data, status=status.HTTP_201_CREATED)

    def __enterprise_processing(self, image_instance, image, *args):
        file_name, file_extension = self.__file_processing(image, image_instance, 400)
        image.save(f".{file_name}_400px_thumbnail{file_extension}")
        file_name, file_extension = self.__file_processing(image, image_instance, 200)
        image.save(f".{file_name}_200px_thumbnail{file_extension}")
        data = {'400px_thumbnail': f'{file_name}_400px_thumbnail{file_extension}',
                '200px_thumbnail': f'{file_name}_200px_thumbnail{file_extension}',
                'original_image': image_instance.original_image.url,
                'expiring_link': "",
                'success': 'Image uploaded successfully'}
        return Response(data, status=status.HTTP_201_CREATED)

    def __default_processing(self, image_instance, image, user):
        file_name, file_extension = self.__file_processing(image, image_instance, user.tier.thumbnail_height)
        image.save(f".{file_name}_{user.tier.thumbnail_height}px_thumbnail{file_extension}")
        data = {f'{str(user.tier.thumbnail_height)}px_thumbnail': f'{file_name}_{str(user.tier.thumbnail_height)}px_thumbnail{file_extension}'}
        if user.tier.presence_of_original_file_link:
            data["original_image"] = image_instance.original_image.url
        if user.tier.ability_to_fetch_expiring_link:
            pass  # todo: implement expiring link
        data["success"] = "Image uploaded successfully"
        return Response(data, status=status.HTTP_201_CREATED)

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
        if serializer.is_valid():
            serializer.save()
            image_absolute_path = image_instance.original_image.path
            with PILImage.open(image_absolute_path) as image:
                return self.options.get(user.tier.name, self.__default_processing)(image_instance, image, user)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
