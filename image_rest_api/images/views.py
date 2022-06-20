import os.path
import time

from django.http import HttpResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist

from .models import Image, ExpiringImage
from .serializer import ImageSerializer
from PIL import Image as PILImage


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def media_access(request, user_pk, image_pk, file_name):
    """
    Access to image file from media folder.
    """
    user = request.user
    if user.pk != user_pk:
        return Response({'error': 'You do not have access to this image'}, status=status.HTTP_403_FORBIDDEN)
    try:
        image = Image.objects.get(pk=image_pk)
    except ObjectDoesNotExist:
        return Response({'error': 'Image does not exist'}, status=status.HTTP_404_NOT_FOUND)
    file_path = os.path.join(os.path.dirname(image.original_image.path), file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            image_data = f.read()
            return HttpResponse(image_data, content_type='image/jpeg')
    return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def expiring_media_access(request, expiring_image_pk, file_name):
    """
    Access to image file from media expiring folder.
    """
    try:
        image = ExpiringImage.objects.get(pk=expiring_image_pk)
    except ObjectDoesNotExist:
        return Response({'error': 'Image does not exist'}, status=status.HTTP_404_NOT_FOUND)
    current_time = int(time.time())  # current time in seconds
    image_time = int(image.created_at.timestamp())  # image time in seconds
    if current_time - image_time > int(image.live_time):  # if image is expired
        image.delete()
        return Response({'error': 'Image has expired'}, status=status.HTTP_404_NOT_FOUND)
    file_path = os.path.join(os.path.dirname(image.image.path), file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            image_data = f.read()
            return HttpResponse(image_data, content_type='image/jpeg')
    return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)


class ImageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = {'Basic': self.__basic_tier_processing,
                        'Premium': self.__premium_tier_processing,
                        'Enterprise': self.__enterprise_tier_processing}

    def __file_processing(self, image, image_instance, size):
        original_image_url = image_instance.original_image.url
        file_name, file_extension = os.path.splitext(original_image_url)
        image.thumbnail((image.width, size))
        return file_name, file_extension

    def __basic_tier_processing(self, image_instance, image, *args):
        file_name, file_extension = self.__file_processing(image, image_instance, 200)
        image.save(f".{file_name}_200px_thumbnail{file_extension}")
        data = {'200px_thumbnail': f'{file_name}_200px_thumbnail{file_extension}',
                'success': 'Image uploaded successfully'}
        return Response(data, status=status.HTTP_201_CREATED)

    def __premium_tier_processing(self, image_instance, image, *args):
        file_name, file_extension = self.__file_processing(image, image_instance, 400)
        image.save(f".{file_name}_400px_thumbnail{file_extension}")
        file_name, file_extension = self.__file_processing(image, image_instance, 200)
        image.save(f".{file_name}_200px_thumbnail{file_extension}")
        data = {'400px_thumbnail': f'{file_name}_400px_thumbnail{file_extension}',
                '200px_thumbnail': f'{file_name}_200px_thumbnail{file_extension}',
                'original_image': image_instance.original_image.url,
                'success': 'Image uploaded successfully'}
        return Response(data, status=status.HTTP_201_CREATED)

    def __enterprise_tier_processing(self, image_instance, image, user, expiration_time, *args):
        # if int(expiration_time) < 300 or int(expiration_time) > 3000:
        #     return Response({'error': 'Expiration time must be between 300 and 3000'},
        #                     status=status.HTTP_400_BAD_REQUEST)
        original_image_url = image_instance.original_image.url
        file_name = os.path.splitext(os.path.basename(original_image_url))[0]
        expiring_image = ExpiringImage.objects.create(user=user, live_time=expiration_time)
        expiring_image.image.save(f'{file_name}_{expiring_image.live_time}s_expiring_image.jpg', image_instance.original_image)
        file_name, file_extension = self.__file_processing(image, image_instance, 400)
        image.save(f".{file_name}_400px_thumbnail{file_extension}")
        file_name, file_extension = self.__file_processing(image, image_instance, 200)
        image.save(f".{file_name}_200px_thumbnail{file_extension}")
        data = {'400px_thumbnail': f'{file_name}_400px_thumbnail{file_extension}',
                '200px_thumbnail': f'{file_name}_200px_thumbnail{file_extension}',
                'original_image': image_instance.original_image.url,
                f'{expiration_time}s_expiring_link': expiring_image.image.url,
                'success': 'Image uploaded successfully'}
        return Response(data, status=status.HTTP_201_CREATED)

    def __default_tier_processing(self, image_instance, image, user):
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
            original_image_path = image_instance.original_image.path
            expiration_time = request.data['expiration_time']  # expiring link live time
            with PILImage.open(original_image_path) as image:
                return self.options.get(user.tier.name, self.__default_tier_processing)(image_instance, image, user, expiration_time)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
