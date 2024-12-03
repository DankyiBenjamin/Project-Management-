from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/comments/<int:project_id>/', consumers.CommentConsumer.as_asgi()),
]
# are they supposed to match with the urls?
# Not Found: /ws/comments/3/
# [02/Dec/2024 22:11:41] "GET /ws/comments/3/ HTTP/1.1" 404 7191
# [02/Dec/2024 22:11:46] "POST /project/3/comments/ HTTP/1.1" 200 87
