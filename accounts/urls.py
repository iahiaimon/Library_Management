from django.urls import path
from .views import (
    register,
    student_register,
    librarian_register,
    login_view,
    student_login,
    librarian_login,
    librarian_dashboard,
    student_dashboard,
    logout_view
)


urlpatterns = [
    path("register/", register, name="register"),
    path("register/student", student_register, name="register_student"),
    path("register/librarian", librarian_register, name="register_librarian"),


    path("login/", login_view, name="login"),
    path("login/student", student_login, name="student_login"),
    path("login/librarian", librarian_login, name="librarian_login"),
    path("logout/", logout_view, name="logout"),

    path("student_dashboard/" , student_dashboard , name="student_dashboard"),
    path("librarian_dashboard/" , librarian_dashboard , name="librarian_dashboard")
]


# urlpatterns = [
#     # Authentication URLs (Phase 4)
#     path('', views.home, name='home'),
#     path('register/', views.register, name='register'),
#     path('login/', views.login_view, name='login'),
#     path('logout/', views.logout_view, name='logout'),

#     # Dashboard URLs (phase 5)
#     path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
#     path('dashboard/librarian/', views.librarian_dashboard, name='librarian_dashboard'),
#     path('dashboard/student/', views.student_dashboard, name='student_dashboard'),

#     # Admin Approval URLs (phase 5)
#     path('approvals/approve/<int:user_id>/', views.approve_user, name='approve_user'),
#     path('approvals/reject/<int:user_id>/', views.reject_user, name='reject_user'),

#     # Book URLs  (phase 1)
#     path('books/', views.book_list, name='book_list'),

#     # Book URLs  (phase 2)
#     path('books/create/', views.create_book, name='create_book'),
#     path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
#     path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),

#     # Student URLs (phase 3)
#     path('students/', views.student_list, name='student_list'),
#     path('students/create/', views.create_student, name='create_student'),
#     path('students/<int:pk>/', views.student_detail, name='student_detail'),
#     path('students/<int:pk>/edit/', views.edit_student, name='edit_student'),
#     path('students/<int:pk>/delete/', views.delete_student, name='delete_student'),

#     # Issue/Return URLs (phase 3)
#     path('issued-books/', views.issued_books_list, name='issued_books_list'),
#     path('issued-books/issue/', views.issue_book, name='issue_book'),
#     path('issued-books/<int:pk>/return/', views.return_book, name='return_book'),
# ]
