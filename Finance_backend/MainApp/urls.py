from django.urls import path,include
from . import views
urlpatterns = [

    path('',views.dashboard,name='dashboard'),

    path('adminpage',views.adminpage,name='adminpage'),
    path('adminpage/user_details/',views.user_details,name='user_details'),
    path('adminpage/edit_user/<int:id>',views.edit_user,name='edit_user'),
    path('adminpage/delete_user/<int:id>',views.delete_user,name='delete_user'),
    path('adminpage/finance_records/',views.finance_records,name='finance_records'),
    path('adminpage/edit_finance/<int:id>',views.edit_finance,name='edit_finance'),
    path('adminpage/delete_finance/<int:id>',views.delete_finance,name='delete_finance'),


]
