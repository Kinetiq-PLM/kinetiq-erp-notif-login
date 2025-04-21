import boto3
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

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
    
@csrf_exempt
def send_notif(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print('Creating notif...')
        origin_module =  data.get('module')
        origin_submodule = data.get('submodule')
        recipient_id = data.get('recipient_id')
        msg = data.get('msg')
        origin_string = origin_module
        if origin_submodule:
            origin_string += '/' + origin_submodule
        print(f'({origin_string}, {recipient_id}, {msg})')
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO admin.notifications (module, to_user_id, message, notifications_status, created_at)
                VALUES
                    (%s, %s, %s, 'Unread', NOW());
            """, [origin_string, recipient_id, msg])
    return JsonResponse({"success": True})

@csrf_exempt
def send_notif_batch(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print('Creating notifs...')
        origin_module =  data.get('module')
        origin_submodule = data.get('submodule')
        recipient_ids = data.get('recipient_ids')
        msg = data.get('msg')
        origin_string = origin_module
        if origin_submodule:
            origin_string += '/' + origin_submodule

        values_query = ''
        args = []

        for i in range(len(recipient_ids)):
            values_query += "(%s, %s, %s, 'Unread', NOW())"
            if (i < len(recipient_ids)-1):
                values_query += ",\n"
            args.append(origin_string)
            args.append(recipient_ids[i])
            args.append(msg)
            print(f'({origin_string}, {recipient_ids[i]}, {msg})')
            
        print(values_query)
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO admin.notifications (module, to_user_id, message, notifications_status, created_at)
                VALUES
                """
                + values_query + ";"
            , args)

    return JsonResponse({"success": True})
    
@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_to_s3(request):
    import json
    data = json.loads(request.body)
    filename = data['filename']
    directory = data['directory']
    content_type = data.get('contentType', 'application/octet-stream')

    key = f"{directory.rstrip('/')}/{filename}"

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    presigned_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': key,
            'ContentType': content_type
        },
        ExpiresIn=300  # 5 minutes
    )

    public_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
    return JsonResponse({'uploadUrl': presigned_url, 'fileUrl': public_url})


@csrf_exempt
@api_view(['GET'])
def retrieve_directory(request):
    directory = request.query_params.get('directory')
    if not directory:
        return Response({"error": "Missing 'directory' query param"}, status=400)

    prefix = directory.rstrip('/') + '/'  # ensure it's formatted like a "folder"

    s3 = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    try:
        response = s3.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=50
        )

        contents = response.get('Contents', [])
        file_urls = [
            f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{item['Key']}"
            for item in contents if not item['Key'].endswith('/')
        ]

        return Response({"files": file_urls})

    except Exception as e:
        return Response({"error": str(e)}, status=500)