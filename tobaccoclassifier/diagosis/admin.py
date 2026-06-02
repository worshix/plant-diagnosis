from django.contrib import admin
from .models import LeafImage


@admin.register(LeafImage)
class LeafImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'actual_disease', 'predicted_disease', 'temperature', 'humidity', 'uploaded_at']
    list_filter = ['actual_disease', 'predicted_disease', 'uploaded_at']
    search_fields = ['notes']
    readonly_fields = ['image_preview', 'uploaded_at', 'predicted_disease', 'confidence_score']
    
    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'
