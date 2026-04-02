from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
# Create your models here.

class FinancialRecord(models.Model):
    TYPE_CHOICES = [
        ('INCOME','INCOME'),
        ('EXPENSES','EXPENSES'),
    ]
    CATEGORY_CHOICES = [
    ('Salary', 'Salary'),
    ('Sales Revenue', 'Sales Revenue'),
    ('Software & Subscriptions', 'Software & Subscriptions'),
    ('Travel', 'Travel'),
    ('Refunds','Refunds'),
    ('Miscellaneous','Miscellaneous'),
    ]
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to=(
            Q(is_staff=True) | 
            Q(is_superuser=True) | 
            Q(groups__name='Admin')
        )
    )
    amount = models.FloatField()
    type = models.CharField(choices=TYPE_CHOICES,max_length=10)
    category =  models.CharField(choices=CATEGORY_CHOICES,max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    short_note =  models.TextField(max_length=150)

    class Meta:
        permissions = [
            ("can_view_summary", "Can view the aggregated dashboard summary"),
        ]
    def __str__(self):
        return f'{self.user} - {self.created_at}'
    

    


