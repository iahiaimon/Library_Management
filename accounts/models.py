from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract base class that provides timestamp fields
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ApprovalMixin(models.Model):
    """
    Abstract base class that provides approval workflow fields
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,  # Index for faster queries
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_approvals",  # Dynamic related name
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")
    rejection_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def approve(self, approved_by_user):
        """Method to approve the record"""
        self.status = "approved"
        self.approved_by = approved_by_user
        self.approval_date = timezone.now()
        self.rejection_reason = ""
        self.rejection_date = None
        self.save()

    def reject(self, rejected_by_user, reason=""):
        """Method to reject the record"""
        self.status = "rejected"
        self.approved_by = rejected_by_user
        self.rejection_reason = reason
        self.rejection_date = timezone.now()
        self.approval_date = None
        self.save()

    def is_pending(self):
        """Check if status is pending"""
        return self.status == "pending"

    def is_approved(self):
        """Check if status is approved"""
        return self.status == "approved"

    def is_rejected(self):
        """Check if status is rejected"""
        return self.status == "rejected"

class UserProfile(TimestampedModel, ApprovalMixin):
    """
    Unified profile model for both students and librarians
    Inherits timestamp and approval functionality from abstract classes
    """

    ROLE_CHOICES = [
        ("student", "Student"),
        ("librarian", "Librarian"),
    ]

    DEPARTMENT_CHOICES = [
        ("CSE", "Computer Science & Engineering"),
        ("EEE", "Electrical & Electronic Engineering"),
        ("ICT", "Information & Communication Technology"),
        ("Robotics", "Robotics & Automation"),
        ("Cyber_Security", "Cyber Security"),
    ]

    # Core fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student",
        db_index=True,  # Index for filtering by role
    )

    # Common fields
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20)

    # Student-specific fields (optional for librarians)
    id_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Required for students",
    )
    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES,
        null=True,
        blank=True,
        db_index=True,  # Index for filtering by department
        help_text="Required for students",
    )

    def __str__(self):
        if self.role == "student":
            return f"{self.name} ({self.id_number}) - {self.get_status_display()}"
        return f"{self.name} (Librarian) - {self.get_status_display()}"

    def clean(self):
        """Validate that students have required fields"""
        super().clean()

        if self.role == "student":
            if not self.id_number:
                raise ValidationError(
                    {"id_number": "ID number is required for students"}
                )
            if not self.department:
                raise ValidationError(
                    {"department": "Department is required for students"}
                )

        # Validate email matches user email if user exists
        if self.user_id and self.email != self.user.email:
            raise ValidationError(
                {"email": "Email must match the associated user account email"}
            )

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == "student"

    @property
    def is_librarian(self):
        """Check if user is a librarian"""
        return self.role == "librarian"

    @property
    def can_issue_books(self):
        """Check if user can issue books (approved students only)"""
        return self.is_student and self.is_approved()

    @property
    def can_manage_library(self):
        """Check if user can manage library (approved librarians only)"""
        return self.is_librarian and self.is_approved()

    def get_full_info(self):
        """Return formatted full information"""
        info = {
            "name": self.name,
            "email": self.email,
            "phone": self.phone_number,
            "role": self.get_role_display(),
            "status": self.get_status_display(),
        }

        if self.is_student:
            info.update(
                {
                    "id_number": self.id_number,
                    "department": self.get_department_display(),
                }
            )

        return info

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            models.Index(
                fields=["role", "status"]
            ),  # Composite index for common queries
            models.Index(fields=["department", "status"]),
        ]
