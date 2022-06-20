from django.db import models


def upload_location(instance, filename, **kwargs):
    """
    Location for the image file
    """
    file_path = f'{instance.user.id}/images/{filename}'
    return file_path


class Image(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to=upload_location)
    date_added = models.DateTimeField(auto_now_add=True)
    expiration_time = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.original_image.url
