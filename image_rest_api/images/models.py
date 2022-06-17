from django.db import models


class Image(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to='images/')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_image.url
