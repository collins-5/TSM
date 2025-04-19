# tenders/admin.py
from django.contrib import admin
from .models import Tender, TenderCategory, TenderStage, TenderDocument

class TenderDocumentInline(admin.TabularInline):
    model = TenderDocument
    extra = 1

@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'title', 'created_by', 'submission_deadline', 'is_active']
    list_filter = ['is_active', 'categories', 'current_stage']
    search_fields = ['title', 'reference_number', 'description']
    date_hierarchy = 'created_at'
    inlines = [TenderDocumentInline]

@admin.register(TenderCategory)
class TenderCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(TenderStage)
class TenderStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']
    search_fields = ['name']

@admin.register(TenderDocument)
class TenderDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'tender', 'uploaded_at', 'is_public']
    list_filter = ['is_public', 'uploaded_at']
    search_fields = ['title', 'tender__title']