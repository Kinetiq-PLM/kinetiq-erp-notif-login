from django.urls import path
from .views import NotifView, upload_to_s3, retrieve_directory, send_notif, send_notif_batch
  
urlpatterns = [
    path('notifications/', NotifView.as_view(), name='notifications'),
    path('upload-to-s3/', upload_to_s3, name='upload_to_s3'),
    path('retrieve-s3-directory/', retrieve_directory, name='retrieve_directory'),
    path('send-notif/', send_notif, name='send_notif'),
    path('send-notif-batch/', send_notif_batch, name='send_notif_batch')
    
]