from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    quantity = models.IntegerField(default=1)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True, help_text="Upload a book cover image (JPG, PNG)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ('CSE', 'CSE'),
        ('EEE', 'EEE'),
        ('ICT', 'ICT'),
        ('Robotics', 'Robotics'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    id_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.id_number})"

    class Meta:
        ordering = ['id_number']


class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='librarian_profile')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} (Librarian)"

    class Meta:
        ordering = ['-created_at']


class IssuedBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='issued_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issued_to')
    quantity = models.IntegerField(default=1)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book.title} - {self.student.name}"

    class Meta:
        ordering = ['-issue_date']


class UserApproval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('librarian', 'Librarian'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='approval_record')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approvals_given')
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')
    rejection_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role}) - {self.status}"

    class Meta:
        ordering = ['-created_at']
