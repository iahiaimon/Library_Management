from django.db import models
from django.utils import timezone


from accounts.models import UserProfile


# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    quantity = models.IntegerField(default=1)
    cover_image = models.ImageField(
        upload_to="book_covers/",
        null=True,
        blank=True,
        help_text="Upload a book cover image (JPG, PNG)",
        default="book_covers/DaVinciCode.jpg",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class IssuedBook(models.Model):
    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="issued_books",
        limit_choices_to={"role": "student"},  # Ensure only students can be selected
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issued_to")
    quantity = models.IntegerField(default=1)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book.title} - {self.student.name}"

    class Meta:
        ordering = ["-issue_date"]
