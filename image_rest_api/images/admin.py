from django.contrib import admin

from .models import Image, ExpiringImage

admin.site.register(Image)
admin.site.register(ExpiringImage)
