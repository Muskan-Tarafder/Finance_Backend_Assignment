from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
import jwt
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import authenticate
import json
import datetime
def home(request):
    if request.method == 'GET':
        context = {
            'Status': 'Can perform Login',
        }
        return JsonResponse(context)
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                payload = {
                    'user_id': user.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1), # Expires in 24 hours
                    'iat': datetime.datetime.utcnow() # Issued at
                }
                
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                
                return JsonResponse({
                    'token': token, 
                    'message': 'Login successful',
                    'role': list(user.groups.values_list('name', flat=True)) 
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)
