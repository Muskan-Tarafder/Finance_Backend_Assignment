from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.forms.models import model_to_dict
from functools import wraps
from django.db.models import Sum
import jwt
from django.db.models.functions import TruncMonth, TruncWeek
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.


# ================
# Helper Functions
# ================

def category_calculation():
    category_wise = FinancialRecord.objects.filter(type='EXPENSES') \
    .values('category') \
    .annotate(total_spent=Sum('amount')) \
    .order_by('-total_spent')

    formatted_breakdown_expense = []
    for item in category_wise:
        formatted_breakdown_expense.append({
            "category": item['category'],
            "total_spent": str(item['total_spent'])
        })
    category_wise = FinancialRecord.objects.filter(type='INCOME') \
    .values('category') \
    .annotate(total_spent=Sum('amount')) \
    .order_by('-total_spent')

    formatted_breakdown_income = []
    for item in category_wise:
        formatted_breakdown_income.append({
            "category": item['category'],
            "total_spent": str(item['total_spent'])
        })
    return {'Expense_category': formatted_breakdown_expense, 'Income_category': formatted_breakdown_income}



def trend_calculation():

    monthly_income_qs = FinancialRecord.objects.filter(type='INCOME') \
        .annotate(month=TruncMonth('created_at')) \
        .values('month') \
        .annotate(total=Sum('amount')) \
        .order_by('month')

    monthly_expense_qs = FinancialRecord.objects.filter(type='EXPENSES') \
        .annotate(month=TruncMonth('created_at')) \
        .values('month') \
        .annotate(total=Sum('amount')) \
        .order_by('month')

    monthly_trends = {
        "income": [{"period": item['month'].strftime('%Y-%m'), "total": str(item['total'])} for item in monthly_income_qs if item['month']],
        "expenses": [{"period": item['month'].strftime('%Y-%m'), "total": str(item['total'])} for item in monthly_expense_qs if item['month']]
    }

    weekly_income_qs = FinancialRecord.objects.filter(type='INCOME') \
        .annotate(week=TruncWeek('created_at')) \
        .values('week') \
        .annotate(total=Sum('amount')) \
        .order_by('week')

    weekly_expense_qs = FinancialRecord.objects.filter(type='EXPENSES') \
        .annotate(week=TruncWeek('created_at')) \
        .values('week') \
        .annotate(total=Sum('amount')) \
        .order_by('week')

    weekly_trends = {
        "income": [{"period": item['week'].strftime('%Y-%m-%d'), "total": str(item['total'])} for item in weekly_income_qs if item['week']],
        "expenses": [{"period": item['week'].strftime('%Y-%m-%d'), "total": str(item['total'])} for item in weekly_expense_qs if item['week']]
    }

    return {
        "monthly": monthly_trends,
        "weekly": weekly_trends
    }


def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 1. Look for the token in the headers
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized. Missing Bearer token.'}, status=401)
            
        token = auth_header.split(' ')[1] 
        
        try:
            # 2. Decode the token (Automatically checks if it's expired or tampered with)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # 3. MAGIC TRICK: Fetch the user and attach them to the request!
            user = User.objects.get(id=payload['user_id'])
            request.user = user 
            
            return view_func(request, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired. Please log in again.'}, status=401)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return JsonResponse({'error': 'Invalid token.'}, status=401)
            
    return _wrapped_view

# =========
# Dashboard
# =========

@jwt_required
def dashboard(request):
    total_income = FinancialRecord.objects.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = FinancialRecord.objects.filter(type='EXPENSES').aggregate(Sum('amount'))['amount__sum'] or 0
    
    net_balance = total_income - total_expenses


    recent_transactions = list(
        FinancialRecord.objects.order_by('-id')[:5].values(
                'id','amount', 'type', 'category'
        )
    )

    formatted_breakdown = category_calculation()
    trends = trend_calculation()
    
    dashboard_data = {
            "summary": {
                "total_income": str(total_income),     
                "total_expenses": str(total_expenses),
                "net_balance": str(net_balance)
            },
            "recent_transactions": recent_transactions,
            "category_total":formatted_breakdown,
            'trends':trends,
        }
    return JsonResponse({'data': dashboard_data})



# ==============
# Analyst Access
# ==============

@jwt_required
def expense_list(request):
    print("User's groups are:", list(request.user.groups.values_list('name', flat=True)))
    
    if not request.user.groups.filter(name='Viewers').exists():
        expense_list = FinancialRecord.objects.filter(type='EXPENSES').values('id','amount', 'category', 'short_note', 'created_at')
        total_expense = FinancialRecord.objects.filter(type='EXPENSES').aggregate(Sum('amount'))['amount__sum'] or 0

        context = {
            'list': list(expense_list),
            'total_expense': str(total_expense),
        }
        return JsonResponse(context)
    else:
        return JsonResponse({'error': 'Viewers do not have access to this API.'}, status=403)
    

@jwt_required
def income_list(request):
    print("User's groups are:", list(request.user.groups.values_list('name', flat=True)))
    
    if not request.user.groups.filter(name='Viewers').exists():
        expense_list = FinancialRecord.objects.filter(type='INCOME').values('id','amount', 'category', 'short_note', 'created_at')
        total_expense = FinancialRecord.objects.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0

        context = {
            'list': list(expense_list),
            'total_expense': str(total_expense),
        }
        return JsonResponse(context)
    else:
        return JsonResponse({'error': 'Viewers do not have access to this API.'}, status=403)
    
@jwt_required
def complete_list(request):
    print("User's groups are:", list(request.user.groups.values_list('name', flat=True)))
    
    if not request.user.groups.filter(name='Viewers').exists():
        full_list = FinancialRecord.objects.all().values('id','amount', 'category', 'short_note', 'created_at')
        paginator = Paginator(full_list, 10) 

        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context = {
            'full_list': list(page_obj),               
            'pagination': {
                'total_records': paginator.count,      
                'total_pages': paginator.num_pages,    
                'current_page': page_obj.number,       
                'has_next': page_obj.has_next(),       
                'has_previous': page_obj.has_previous()
            }
        }
        return JsonResponse(context)
    else:
        return JsonResponse({'error': 'Viewers do not have access to this API.'}, status=403)
    

@jwt_required
def category_list(request,category,type):
    print("User's groups are:", list(request.user.groups.values_list('name', flat=True)))
    
    if not request.user.groups.filter(name='Viewers').exists():
        cat_list =  FinancialRecord.objects.filter(type=type,category=category).values('id','amount', 'category', 'short_note', 'created_at')  

        context = {
            'full_list': list(cat_list),
        }
        return JsonResponse(context)
    else:
        return JsonResponse({'error': 'Viewers do not have access to this API.'}, status=403)
    
    




# ==========
# Admin Page
# ==========

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Rule A: Are they logged in?
            
        # Rule B: Are they an Admin? (Checking group name or superuser status)
        is_admin = request.user.groups.filter(name='Admin').exists() or request.user.is_superuser
        if not is_admin:
            return JsonResponse({'error': 'Forbidden. Admins only.'}, status=403)
            
        # If they pass both rules, let them in!
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@jwt_required
@admin_required
def adminpage(request):
    context = {
        'Users':'Users and Roles',
        'Records':'Records',

    }
    return JsonResponse(context)

@jwt_required
@admin_required
def user_details(request):
    data = list(User.objects.all().values('id', 'username', 'email'))
    context = {
        'data':data,
    }
    return JsonResponse(context)

@csrf_exempt
@jwt_required
@admin_required
def add_user(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            user = User.objects.create_user(
                    username=data['username'],
                    email=data.get('email', ''),
                    password=data['password']
                )
        if 'role' in data:
            group = Group.objects.get(name=data['role'])
            user.groups.add(group)
                
        return JsonResponse({'message': 'User created successfully', 'id': user.id}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@jwt_required
@admin_required
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


@csrf_exempt
@jwt_required
@admin_required
def delete_user(request,id):
    user = get_object_or_404(User,pk=id)
    user.delete()
    return JsonResponse({'message':'Deleted Successfully'})


@jwt_required
@admin_required
def finance_records(request):
    data = list(FinancialRecord.objects.all().values())
    context = {
        'data':data,
    }
    return JsonResponse(context)


@csrf_exempt
@jwt_required
@admin_required
def add_finance(request):
    if request.method=='POST':
        try:
            data = json.loads(request.body)
            form = AddFinanceRecord(data)
            if form.is_valid():
                form.save()
                return JsonResponse({'message':'New Record Created'})
            else:
                return JsonResponse({'error':form.error},status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error':'Invalid Payload'},status=400)

      
@csrf_exempt
@jwt_required 
@admin_required
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
@jwt_required
@admin_required
def delete_finance(request,id):
    if request.method == 'DELETE':
        user = get_object_or_404(FinancialRecord,pk=id)
        user.delete()
        return JsonResponse({'message':'Deleted Successfully'})
    return JsonResponse({'message':'Method wrong'},status=405)



@jwt_required
def filter_record(request):

    if request.user.groups.filter(name='Viewers').exists():
        return JsonResponse({'error': 'Viewers do not have access to this API.'}, status=403)

    records = FinancialRecord.objects.all().order_by('-created_at')

    category = request.GET.get('category')
    record_type = request.GET.get('type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')     # YYYY-MM-DD


    if category:
        records = records.filter(category__iexact=category) 
        
    if record_type:
        records = records.filter(type__iexact=record_type)
        
    if start_date:
        records = records.filter(created_at__lte=start_date) 
        
    if end_date:
        records = records.filter(created_at__lte=end_date)

    filtered_list = records.values('id', 'amount', 'type', 'category', 'short_note', 'created_at')

    paginator = Paginator(filtered_list, 10)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


    context = {
        'results': list(page_obj),
        'pagination': {
            'total_records': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    }
    
    return JsonResponse(context)