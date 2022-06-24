from django.urls import path

from images.views import ImageView

urlpatterns = [
    path("", ImageView.as_view(), name="image-view"),
]
