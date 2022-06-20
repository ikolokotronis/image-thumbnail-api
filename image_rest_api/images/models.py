from django.db import models


def image_upload_location(instance, filename, **kwargs):
    """
    Location for the image file
    """
    file_path = f'{instance.user.id}/images/{filename}'
    return file_path


def expiring_image_upload_location(instance, filename, **kwargs):
    """
    Location for the expiring image file
    """
    file_path = f'expiring_images/{instance.id}/{filename}'
    return file_path


class ExpiringImage(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=expiring_image_upload_location)
    live_time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.image.url


class Image(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to=image_upload_location)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_image.url

    def save(self, *args, **kwargs):
        """
        Override save method to get the pk of the image instance
        """
        if self.pk is None:
            saved_original_image = self.original_image
            self.original_image = None
            super(Image, self).save(*args, **kwargs)
            self.original_image = saved_original_image

        super(Image, self).save(*args, **kwargs)
