from django.db import models
from django.contrib.auth.models import User , AbstractUser
from core.models.time_stamp import TimestampedModel

class CustomUser(TimestampedModel , AbstractUser ):
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

    name = models.CharField(blank=False , null= False , max_length=255)
    email =models.EmailField(unique=True )
    phone = models.CharField( blank= False , null= False , max_length=15)
    institute = models.CharField(blank=False , null= False)
    image = models.ImageField(upload_to="/student_id" , blank=True , null= True ,default="https://static.vecteezy.com/system/resources/thumbnails/014/579/417/small/school-id-card-template-and-vatical-college-student-identity-card-design-layout-free-vector.jpg")
    department = models.CharField(
        choices=DEPARTMENT_CHOICES,
        default = "CST",
        db_index= True,
    )

    role = models.CharField(
        choices=ROLE_CHOICES,
        default="student",
        db_index=True
    )

    def __str__(self):
        if self.role == "student":
            return f"{self.name} ({self.institute})"
        return f"Librarian {self.name} -- {self.email}"