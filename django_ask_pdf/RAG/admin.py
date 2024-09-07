from django.contrib import admin
from .models import File, Chat

# Register your models here.
@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'file', 'created_at', 'chroma_id')  # Customize this as needed

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file', 'message', 'response', 'created_at')  # Customize this as needed