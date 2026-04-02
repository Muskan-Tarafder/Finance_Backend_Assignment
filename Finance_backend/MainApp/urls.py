from django.urls import path,include
from . import views
urlpatterns = [

    path('',views.dashboard,name='dashboard'),
    path('expense_list',views.expense_list,name='expense_list'),
    path('income_list/',views.income_list,name='income_list'),
    path('complete_list/',views.complete_list,name='complete_list'),
    path('category_list/<str:type>/<str:category>/', views.category_list, name='category_list'),
    path('filter_record/',views.filter_record,name='filter_record'),


    path('adminpage',views.adminpage,name='adminpage'),
    path('adminpage/user_details/',views.user_details,name='user_details'),
    path('adminpage/add_user/',views.add_user,name='add_user'),
    path('adminpage/edit_user/<int:id>',views.edit_user,name='edit_user'),
    path('adminpage/delete_user/<int:id>',views.delete_user,name='delete_user'),
    path('adminpage/finance_records/',views.finance_records,name='finance_records'),
    path('adminpage/add_finance/',views.add_finance,name='add_finance'),
    path('adminpage/edit_finance/<int:id>',views.edit_finance,name='edit_finance'),
    path('adminpage/delete_finance/<int:id>',views.delete_finance,name='delete_finance'),


]
