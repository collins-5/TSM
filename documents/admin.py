from django.contrib import admin
from .models import Document, DocumentCategory

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'visibility', 'created_at')
    list_filter = ('visibility', 'category', 'created_at')
    search_fields = ('title', 'description', 'uploaded_by__username')
    date_hierarchy = 'created_at'
    filter_horizontal = ('authorized_users',)