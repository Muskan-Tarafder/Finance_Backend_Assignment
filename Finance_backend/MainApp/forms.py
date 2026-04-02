from django import forms
from django.contrib.auth.models import User
from .models import FinancialRecord

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','is_active','groups')


class EditFinanceRecord(forms.ModelForm):
    class Meta:
        model = FinancialRecord
        fields = '__all__'


class AddFinanceRecord(forms.ModelForm):
    class Meta:
        model = FinancialRecord
        fields = '__all__'