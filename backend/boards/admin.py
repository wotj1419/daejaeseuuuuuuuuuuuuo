from django.contrib import admin
from .models import BoardPost


@admin.register(BoardPost)
class BoardPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'board_type', 'author', 'created_at')
    list_filter = ('board_type', 'created_at')
    search_fields = ('title', 'content', 'author__username')
