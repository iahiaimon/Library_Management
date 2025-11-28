from django.contrib import admin
from django.utils.html import format_html
from .models import Book, Student, IssuedBook, UserApproval

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'quantity', 'cover_preview', 'created_at')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def cover_preview(self, obj):
        """Display cover image thumbnail in admin list"""
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="50" height="75" style="object-fit: cover; border-radius: 4px;" />',
                obj.cover_image.url
            )
        return format_html('<span style="color: #999;">No cover</span>')
    cover_preview.short_description = 'Cover Image'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_number', 'department', 'phone_number', 'created_at')
    search_fields = ('name', 'id_number', 'phone_number')
    list_filter = ('department', 'created_at')
    ordering = ('id_number',)


@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'student', 'quantity', 'issue_date', 'is_returned', 'return_date')
    search_fields = ('book__title', 'student__name', 'student__roll')
    list_filter = ('is_returned', 'issue_date', 'return_date')
    readonly_fields = ('issue_date', 'created_at', 'updated_at')
    ordering = ('-issue_date',)


@admin.register(UserApproval)
class UserApprovalAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status', 'created_at', 'approval_date')
    search_fields = ('user__username', 'user__email')
    list_filter = ('status', 'role', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
