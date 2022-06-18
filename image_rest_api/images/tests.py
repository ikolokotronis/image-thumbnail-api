from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from images.models import Image
from users.models import User, Tier


class ImageTests(APITestCase):
    def setUp(self):
        tier = Tier.objects.create(name='Basic', thumbnail_height=100,
                                   presence_of_original_file_link=True,
                                   ability_to_fetch_expiring_link=False)
        user = User.objects.create_user(username='test', password='test', tier=tier)
        image = SimpleUploadedFile(name='test_image.jpg',
                                   content=open('images/test_images/test.jpg', 'rb').read(),
                                   content_type='image/jpg')
        Image.objects.create(original_image=image, user=user)

    def test_get_all_images(self):
        token = Token.objects.get(user__username='test')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('image-view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Image.objects.count(), 1)

    def test_upload_image(self):
        token = Token.objects.get(user__username='test')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('image-view')
        image = SimpleUploadedFile(name='test_image.jpg',
                                   content=open('images/test_images/test.jpg', 'rb').read(),
                                   content_type='image/jpg')
        data = {'original_image': image}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Image.objects.count(), 2)
