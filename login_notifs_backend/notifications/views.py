from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer

# Create your views here.
class NotifView(APIView):
    def get(self, request):
        
        req_user_id = str(request.query_params.get('user_id'))
        print(f'(notifs dbg) Notif view get with user id {req_user_id}')
        print(f'(notifs dbg) user_id type: {type(req_user_id)}, value: {repr(req_user_id)}')
        notifs = Notification.objects.filter(to_user_id=req_user_id.strip())
        print(f'(notifs dbg) generated query: {notifs.query}')
        serializer = NotificationSerializer(notifs, many = True)
        print('(notifs dbg)', notifs)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        notif_id = request.data.get('notifications_id')
        notif = Notification.objects.get(notifications_id=notif_id)
        notif.notifications_status = 'Read'
        notif.save()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)