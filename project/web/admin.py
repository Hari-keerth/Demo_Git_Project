# from django.contrib import admin
# from .models import Register
# Register your models here.

# admin.site.register(Register)

from django.contrib import admin
from .models import RecruiterJob  # 🟢 Import your job model

# Tell Django admin to display RecruiterJob on the dashboard
admin.site.register(RecruiterJob)