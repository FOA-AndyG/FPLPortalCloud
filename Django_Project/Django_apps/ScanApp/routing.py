from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/ScanApp/(?P<trailer_number>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
