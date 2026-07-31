# from django.contrib import admin
# from .models import Register
# Register your models here.

# admin.site.register(Register)

from django.contrib import admin
from .models import RecruiterJob, Application  # 🟢 Import your job model

# Tell Django admin to display RecruiterJob on the dashboard
admin.site.register(RecruiterJob)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'applied_at')
    search_fields = ('applicant__username', 'job__title')