import os
from datetime import datetime
from typing import Callable

from django.contrib.auth.models import AbstractUser
from django.http import HttpResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist

from .models import Image, ExpiringImage
from .serializer import ImageSerializer
from PIL import Image as PILImage


class ImageAccess(APIView):
    """
    Image access management.
    Only the owner of the image can access the image, if it exists.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def __authorize_user(self, request: Request, user_pk: str) -> AbstractUser | bool:
        user = request.user
        if user.pk == user_pk:
            return user
        return False

    def __get_file_path(self, request: Request, file_name: str) -> str:
        user = request.user
        try:
            image = Image.objects.get(original_image=f"{user.id}/images/{file_name}")
            file_path = os.path.join(
                os.path.dirname(image.original_image.path), file_name
            )
        except ObjectDoesNotExist:
            file_path = self.__find_other_matching_file(request, file_name)
        return file_path

    def __find_other_matching_file(self, request: Request, file_name: str) -> str:
        user = request.user
        images_dir = os.listdir(os.path.join(f"{os.getcwd()}/media/{user.id}/images/"))
        file_path = ""
        for img_file in images_dir:
            if img_file == file_name:
                file_path = os.path.join(
                    f"{os.getcwd()}/media/{user.id}/images/{img_file}"
                )
        return file_path

    def __handle_open_file(self, file_path: str) -> HttpResponse | Response:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                image_data = f.read()
                return HttpResponse(image_data, content_type="image/jpeg")
        return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request: Request, user_pk: str, file_name: str) -> Response:
        if not self.__authorize_user(request, user_pk):
            return Response(
                {"error": "You do not have access to this image"},
                status=status.HTTP_403_FORBIDDEN,
            )
        file_path = self.__get_file_path(request, file_name)
        return self.__handle_open_file(file_path)


class ExpiringImageAccess(APIView):
    """
    Expiring image access management.
    Anyone can access the image can access the image, if it exists and it's not expired.
    """

    def __handle_image_is_expired(self, image: ExpiringImage) -> bool:
        current_time_in_seconds = int(datetime.now().timestamp())
        image_time_in_seconds = int(image.created_at.timestamp())
        if current_time_in_seconds - image_time_in_seconds > int(image.live_time):
            return True
        return False

    def __handle_open_file(self, file_path: str) -> HttpResponse | Response:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                image_data = f.read()
                return HttpResponse(image_data, content_type="image/jpeg")
        return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request: Request, file_name: str) -> Response | Callable:
        try:
            image = ExpiringImage.objects.get(image=f"expiring-images/{file_name}")
        except ObjectDoesNotExist:
            return Response(
                {"error": "Image does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        if self.__handle_image_is_expired(image):
            image.delete()
            return Response(
                {"error": "Image has expired"}, status=status.HTTP_404_NOT_FOUND
            )
        file_path = os.path.join(os.path.dirname(image.image.path), file_name)
        return self.__handle_open_file(file_path)


class ImageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.options = {
            "Basic": self.__basic_tier_processing,
            "Premium": self.__premium_tier_processing,
            "Enterprise": self.__enterprise_tier_processing,
        }

    def __file_processing(self, request: Request, image_instance: Image, image: PILImage, size: int) -> tuple:
        """
        Processes image, returns file url and file extension.
        """
        original_image_url = image_instance.original_image.url
        file_url, file_extension = os.path.splitext(original_image_url)
        image.thumbnail((image.width, size))
        image.save(f".{file_url}_{size}px_thumbnail{file_extension}")
        return file_url, file_extension

    def __basic_tier_processing(self, request: Request, image_instance: Image, image: PILImage) -> Response:
        """
        Basic tier processing.
        """
        file_url, file_extension = self.__file_processing(
            request, image_instance, image, 200
        )
        data = {
            "200px_thumbnail": f"{file_url}_200px_thumbnail{file_extension}",
            "success": "Image uploaded successfully",
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def __premium_tier_processing(self, request: Request, image_instance: Image, image: PILImage) -> Response:
        """
        Premium tier processing.
        """
        file_url, file_extension = self.__file_processing(
            request, image_instance, image, 400
        )
        file_url, file_extension = self.__file_processing(
            request, image_instance, image, 200
        )
        data = {
            "400px_thumbnail": f"{file_url}_400px_thumbnail{file_extension}",
            "200px_thumbnail": f"{file_url}_200px_thumbnail{file_extension}",
            "original_image": image_instance.original_image.url,
            "success": "Image uploaded successfully",
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def __enterprise_tier_processing(self, request: Request, image_instance: Image, image: PILImage) -> Response:
        """
        Enterprise tier processing.
        """
        try:
            live_time = request.data["live_time"]
        except KeyError:
            return Response(
                {"error": "No live_time field"}, status=status.HTTP_400_BAD_REQUEST
            )
        if int(live_time) < 300 or int(live_time) > 3000:
            return Response(
                {"error": "Live time must be between 300 and 3000 seconds"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        original_image_url = image_instance.original_image.url
        file_url, file_extension = self.__file_processing(
            request, image_instance, image, 400
        )
        file_url, file_extension = self.__file_processing(
            request, image_instance, image, 200
        )
        file_name = os.path.splitext(os.path.basename(original_image_url))[0]
        expiring_image = ExpiringImage.objects.create(
            user=request.user, live_time=live_time
        )
        expiring_image.image.save(
            f"{file_name}{file_extension}", image_instance.original_image
        )
        data = {
            "400px_thumbnail": f"{file_url}_400px_thumbnail{file_extension}",
            "200px_thumbnail": f"{file_url}_200px_thumbnail{file_extension}",
            "original_image": original_image_url,
            f"{live_time}s_expiring_link": expiring_image.image.url,
            "success": "Image uploaded successfully",
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def __default_tier_processing(self, request: Request, image_instance: Image, image: PILImage) -> Response:
        """
        Default tier processing. (for arbitrary tiers)
        """
        user = request.user
        file_url, file_extension = self.__file_processing(
            request, image_instance, image, user.tier.thumbnail_height
        )
        file_name = os.path.basename(file_url)
        data = {
            f"{str(user.tier.thumbnail_height)}px_thumbnail": f"{file_url}_{str(user.tier.thumbnail_height)}px_thumbnail{file_extension}"
        }
        if user.tier.presence_of_original_file_link:
            data["original_image"] = image_instance.original_image.url
        if user.tier.ability_to_fetch_expiring_link:
            try:
                live_time = request.data["live_time"]
            except KeyError:
                return Response(
                    {"error": "No live_time field"}, status=status.HTTP_400_BAD_REQUEST
                )
            if int(live_time) < 300 or int(live_time) > 3000:
                return Response(
                    {"error": "Live time must be between 300 and 3000 seconds"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            expiring_image = ExpiringImage.objects.create(
                user=user, live_time=live_time
            )
            expiring_image.image.save(
                f"{file_name}{file_extension}", image_instance.original_image
            )
            data[f"{live_time}s_expiring_link"] = expiring_image.image.url
        data["success"] = "Image uploaded successfully"
        return Response(data, status=status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        """
        Lists all images.
        """
        images = Image.objects.filter(user_id=request.user.id)
        if images:
            serializer = ImageSerializer(images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"No images found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request: Request) -> Response | Callable:
        """
        Calls the appropriate tier processing method and returns the response.
        """
        user = request.user
        image_instance = Image(user=user)
        serializer = ImageSerializer(image_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            image_format = os.path.splitext(image_instance.original_image.url)[1]
            if image_format not in [".jpg", ".jpeg", ".png"]:
                image_instance.delete()
                return Response(
                    {"error": "Image format not supported"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            original_image_path = image_instance.original_image.path
            with PILImage.open(original_image_path) as image:
                return self.options.get(user.tier.name, self.__default_tier_processing)(request, image_instance, image)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
