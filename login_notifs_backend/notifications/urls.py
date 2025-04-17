from django.urls import path
from .views import NotifView, send_notif

urlpatterns = [
    path('notifications/', NotifView.as_view(), name='notifications'),
    path('send-notif/', send_notif, name='send_notif')
]