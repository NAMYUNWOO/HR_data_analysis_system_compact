from django.contrib import admin
from index.models import EmployeeBiography, EmployeeGrade, Education,EmailData, EmailLog
# Register your models here.

admin.site.register(EmployeeBiography)
admin.site.register(EmployeeGrade)
admin.site.register(Education)
admin.site.register(EmailLog)
