from django.contrib import admin
from contents import models
# Register your models here.

admin.site.register(models.ContentCategory)
admin.site.register(models.Content)
