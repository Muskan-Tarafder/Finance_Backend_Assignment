from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.forms.models import model_to_dict
from functools import wraps
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncWeek
# Create your views here.

# =========
# Dashboard
# =========

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
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)




# ==========
# Admin Page
# ==========

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Rule A: Are they logged in?
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized access.'}, status=401)
            
        # Rule B: Are they an Admin? (Checking group name or superuser status)
        is_admin = request.user.groups.filter(name='Admin').exists() or request.user.is_superuser
        if not is_admin:
            return JsonResponse({'error': 'Forbidden. Admins only.'}, status=403)
            
        # If they pass both rules, let them in!
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@admin_required
def adminpage(request):
    context = {
        'Users':'Users and Roles',
        'Records':'Records',

    }
    return JsonResponse(context)

@admin_required
def user_details(request):
    data = list(User.objects.all().values('id', 'username', 'email'))
    context = {
        'data':data,
    }
    return JsonResponse(context)

@csrf_exempt
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
@admin_required
def delete_user(request,id):
    user = get_object_or_404(User,pk=id)
    user.delete()
    return JsonResponse({'message':'Deleted Successfully'})

@admin_required
def finance_records(request):
    data = list(FinancialRecord.objects.all().values())
    context = {
        'data':data,
    }
    return JsonResponse(context)


@csrf_exempt
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
                return JsonResponse({'error':form.error})
        except json.JSONDecodeError:
            return JsonResponse({'error':'Invalid Payload'},status=400)
        
@csrf_exempt
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
@admin_required
def delete_finance(request,id):
    user = get_object_or_404(FinancialRecord,pk=id)
    user.delete()
    return JsonResponse({'message':'Deleted Successfully'})
