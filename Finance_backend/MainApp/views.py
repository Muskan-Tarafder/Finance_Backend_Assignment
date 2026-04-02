from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.forms.models import model_to_dict
# Create your views here.
def dashboard(request):
    pass




# ==========
# Admin Page
# ==========
def adminpage(request):
    context = {
        'Users':'Users and Roles',
        'Records':'Records',

    }
    return JsonResponse(context)

def user_details(request):
    data = list(User.objects.all().values('id', 'username', 'email'))
    context = {
        'data':data,
    }
    return JsonResponse(context)

@csrf_exempt
def edit_user(request,id):
    user = get_object_or_404(User,pk=id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = EditUserForm(data, instance=user)
            
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'User updated successfully', 'status': 200})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
            
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "groups": list(user.groups.values_list('id', flat=True)) 
    }
    
    return JsonResponse({'data': user_data})
    
    return JsonResponse({'data': record_data})

@csrf_exempt
def delete_user(request,id):
    user = get_object_or_404(User,pk=id)
    user.delete()
    return JsonResponse({'message':'Deleted Successfully'})

def finance_records(request):
    data = list(FinancialRecord.objects.all().values())
    context = {
        'data':data,
    }
    return JsonResponse(context)


@csrf_exempt
def add_finance(request):
    if request.method=='POST':
        try:
            data = json.loads(request.body)
            form = AddFinanceRecord(data)
            if form.is_valid():
                form.save()
                return JsonResponse({'message':'New Record Created'})
            else:
                return JsonResponse({'error':form.error})
        except json.JSONDecodeError:
            return JsonResponse({'error':'Invalid Payload'},status=400)
        
@csrf_exempt
def edit_finance(request,id):
    row = get_object_or_404(FinancialRecord,pk=id)
    if request.method == 'PATCH':
        try:
            new_data = json.loads(request.body)
            
            merged_data = model_to_dict(row) 
            
            merged_data.update(new_data)     
            
            form = EditFinanceRecord(merged_data, instance=row)
            
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Record updated successfully', 'status': 200})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    record_data = {
        "user": row.user.id,
        "amount": str(row.amount),
        "type": row.type,
        "category": row.category,
        "short_note": row.short_note
    }
    
    return JsonResponse({'data': record_data})


@csrf_exempt
def delete_finance(request,id):
    user = get_object_or_404(FinancialRecord,pk=id)
    user.delete()
    return JsonResponse({'message':'Deleted Successfully'})
