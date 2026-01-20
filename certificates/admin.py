from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'student', 'course', 'is_approved', 'issued_at', 'approved_at')
    list_filter = ('is_approved', 'issued_at', 'course')
    search_fields = ('certificate_number', 'student__username', 'course__title')
    readonly_fields = ('certificate_number', 'issued_at', 'approved_at')
    actions = ['approve_certificates']
    
    def approve_certificates(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} certificates approved.')
    approve_certificates.short_description = "Approve selected certificates"




