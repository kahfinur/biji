from django.contrib import admin
from .models import Post, AuthPassword, Warga

admin.site.register(Post)

# Register your models here.

admin.site.register(AuthPassword)
admin.site.register(Warga)