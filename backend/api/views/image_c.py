from django.conf import settings
from django.http import HttpResponse, JsonResponse
import django_q.tasks
from rest_framework.decorators import api_view

from ..models import Image
from .utils import (
    _is_image,
    _get_image_original_date,
)


@api_view(['POST'])
def post_image(request):
    f_image = request.FILES['image']
    if _is_image(f_image):
        f_image.seek(0)
        image_original_date = _get_image_original_date(f_image)
        kwargs = {
            'image_path': '',
            'orig_time': image_original_date,
        }
        img = Image.objects.create(**kwargs)
        f_image.seek(0)
        django_q.tasks.async_task('api.tasks.upload_image', f_image.read(), settings.IMGUR_CLIENT_ID, img.id)
        return JsonResponse({"token": img.id})
    return HttpResponse(
        "The uploaded file cannot be parsed to Image",
        status=400,
    )
