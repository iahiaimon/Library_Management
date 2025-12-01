from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import UserProfile


# @admin.register(Book)
# class BookAdmin(admin.ModelAdmin):
#     list_display = (
#         "title",
#         "author",
#         "isbn",
#         "quantity",
#         "cover_preview",
#         "created_at",
#     )
#     search_fields = ("title", "author", "isbn")
#     list_filter = ("created_at", "updated_at")
#     ordering = ("-created_at",)

#     def cover_preview(self, obj):
#         """Display cover image thumbnail in admin list"""
#         if obj.cover_image:
#             return format_html(
#                 '<img src="{}" width="50" height="75" style="object-fit: cover; border-radius: 4px;" />',
#                 obj.cover_image.url,
#             )
#         return format_html('<span style="color: #999;">No cover</span>')

#     cover_preview.short_description = "Cover Image"


# @admin.register(IssuedBook)
# class IssuedBookAdmin(admin.ModelAdmin):
#     list_display = (
#         "book",
#         "student",
#         "quantity",
#         "issue_date",
#         "is_returned",
#         "return_date",
#     )
#     search_fields = ("book__title", "student__name", "student__id_number")
#     list_filter = ("is_returned", "issue_date", "return_date")
#     readonly_fields = ("issue_date", "created_at", "updated_at")
#     ordering = ("-issue_date",)

#     def get_queryset(self, request):
#         """Optimize queries"""
#         qs = super().get_queryset(request)
#         return qs.select_related("book", "student", "student__user")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "role",
        "status_badge",
        "department_info",
        "id_number",
        "phone_number",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "id_number",
        "user__username",
        "phone_number",
    )

    list_filter = (
        "role",
        "status",
        "department",
        "created_at",
        "approval_date",
    )

    readonly_fields = (
        "user",
        "created_at",
        "updated_at",
        "approval_date",
        "rejection_date",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "User Information",
            {"fields": ("user", "name", "email", "phone_number", "role")},
        ),
        (
            "Student Information",
            {
                "fields": ("id_number", "department"),
                "description": "These fields are only required for students",
            },
        ),
        (
            "Approval Status",
            {
                "fields": (
                    "status",
                    "approved_by",
                    "approval_date",
                    "rejection_reason",
                    "rejection_date",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["approve_users", "reject_users", "mark_as_pending"]

    def status_badge(self, obj):
        """Display colored status badge"""
        colors = {
            "pending": "#FFA500",  # Orange
            "approved": "#28A745",  # Green
            "rejected": "#DC3545",  # Red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, "#6C757D"),
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def department_info(self, obj):
        """Display department for students, N/A for librarians"""
        if obj.role == "student" and obj.department:
            return obj.get_department_display()
        return format_html('<span style="color: #999;">N/A</span>')

    department_info.short_description = "Department"

    def approve_users(self, request, queryset):
        """Bulk approve selected users"""
        count = 0
        for profile in queryset.filter(status="pending"):
            # Activate the user account when approving
            profile.user.is_active = True
            profile.user.save()
            profile.approve(request.user)
            count += 1

        self.message_user(request, f"✅ {count} user(s) successfully approved.")

    approve_users.short_description = "✅ Approve selected users"

    def reject_users(self, request, queryset):
        """Bulk reject selected users"""
        count = 0
        for profile in queryset.filter(status="pending"):
            profile.reject(request.user, reason="Rejected by admin")
            count += 1

        self.message_user(
            request, f"❌ {count} user(s) successfully rejected.", level="warning"
        )

    reject_users.short_description = "❌ Reject selected users"

    def mark_as_pending(self, request, queryset):
        """Reset status to pending"""
        count = queryset.update(
            status="pending",
            approval_date=None,
            rejection_date=None,
            approved_by=None,
        )

        self.message_user(request, f"⏳ {count} user(s) marked as pending.")

    mark_as_pending.short_description = "⏳ Mark as pending"

    def get_queryset(self, request):
        """Optimize query with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related("user", "approved_by")

    def save_model(self, request, obj, form, change):
        """Handle user activation when status changes"""
        if change:  # If editing existing profile
            if obj.status == "approved" and not obj.user.is_active:
                obj.user.is_active = True
                obj.user.save()
            elif obj.status in ["pending", "rejected"] and obj.user.is_active:
                obj.user.is_active = False
                obj.user.save()

        super().save_model(request, obj, form, change)
