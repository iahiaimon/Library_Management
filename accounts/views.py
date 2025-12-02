from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserProfile
from .forms import (
    StudentRegistrationForm,
    LibrarianRegistrationForm,
    StudentLoginForm,
    LibrarianLoginForm,
)
from .models import UserProfile





# ============= REGISTRATION VIEWS =============


def register(request):
    """Universal registration view that handles both student and librarian registration"""
    if request.user.is_authenticated:
        return redirect("home")

    # Get role from URL parameter or POST data
    role = request.GET.get("role", "student")

    if request.method == "POST":
        role = request.POST.get("role", "student")

        # Select appropriate form based on role
        if role == "student":
            form = StudentRegistrationForm(request.POST)
        else:
            form = LibrarianRegistrationForm(request.POST)

        if form.is_valid():
            try:
                # Save user and profile (form handles all creation logic)
                user, profile = form.save()

                messages.success(
                    request,
                    f"✅ Account created successfully! Your {role} account is pending admin approval. "
                    "You will be notified once approved.",
                )
                return redirect("login")

            except Exception as e:
                messages.error(
                    request,
                    f"❌ An error occurred during registration: {str(e)}. Please try again.",
                )
    else:
        # GET request - display empty form
        if role == "student":
            form = StudentRegistrationForm()
        else:
            form = LibrarianRegistrationForm()

    context = {
        "form": form,
        "role": role,
        "is_student": role == "student",
        "is_librarian": role == "librarian",
    }

    return render(request, "accounts/register.html", context)


def student_register(request):
    """Direct student registration view"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user, profile = form.save()
                messages.success(
                    request,
                    "✅ Student account created successfully! Please wait for admin approval.",
                )
                return redirect("student_login")
            except Exception as e:
                messages.error(request, f"❌ Registration failed: {str(e)}")
    else:
        form = StudentRegistrationForm()

    return render(request, "accounts/student_register.html", {"form": form})


def librarian_register(request):
    """Direct librarian registration view"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LibrarianRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user, profile = form.save()
                messages.success(
                    request,
                    "✅ Librarian account created successfully! Please wait for admin approval.",
                )
                return redirect("librarian_login")
            except Exception as e:
                messages.error(request, f"❌ Registration failed: {str(e)}")
    else:
        form = LibrarianRegistrationForm()

    return render(request, "accounts/librarian_register.html", {"form": form})


# ============= LOGIN VIEWS =============


def login_view(request):
    """Universal login view (checks role automatically)"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        # Authenticate user using email backend
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Check if user is superuser/admin (bypass approval check)
            if user.is_superuser or user.is_staff:
                login(request, user)

                # Set session expiry
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close

                messages.success(request, f"👋 Welcome back, {user.username}!")
                return redirect("home")

            # For regular users, check if they have a profile
            if not hasattr(user, "profile"):
                messages.error(
                    request,
                    "❌ Your account is not properly configured. Please contact the administrator.",
                )
                return redirect("login")

            profile = user.profile

            # Check approval status
            if profile.status == "pending":
                messages.warning(
                    request,
                    f"⏳ Your {profile.get_role_display()} registration is still pending! "
                    "Please wait for admin approval.",
                )
                return redirect("login")

            elif profile.status == "rejected":
                rejection_msg = (
                    profile.rejection_reason
                    if profile.rejection_reason
                    else "Not specified"
                )
                messages.error(
                    request,
                    f"❌ Your registration has been rejected. Reason: {rejection_msg}. "
                    "Please contact the administrator for more information.",
                )
                return redirect("login")

            elif profile.status == "approved":
                # Check if user account is active
                if not user.is_active:
                    messages.error(
                        request,
                        "❌ Your account has been deactivated. Please contact the administrator.",
                    )
                    return redirect("login")

                # All checks passed - login the user
                login(request, user)

                # Set session expiry
                if not remember_me:
                    request.session.set_expiry(0)

                messages.success(request, f"👋 Welcome back, {profile.name}!")

                # Redirect based on role
                if profile.is_librarian:
                    return redirect("librarian_dashboard")
                else:
                    return redirect("student_dashboard")

            else:
                messages.error(
                    request,
                    "❌ Your account status is unknown. Please contact the administrator.",
                )
                return redirect("login")
        else:
            messages.error(request, "❌ Invalid email or password. Please try again.")

    return render(request, "accounts/login.html")


def student_login(request):
    """Student-specific login view"""
    if request.user.is_authenticated:
        # Check if already logged in user is a student
        if hasattr(request.user, "profile") and request.user.profile.is_student:
            return redirect("student_dashboard")
        return redirect("home")

    if request.method == "POST":
        form = StudentLoginForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data["user"]
            remember_me = form.cleaned_data.get("remember_me", False)

            login(request, user)

            # Set session expiry
            if not remember_me:
                request.session.set_expiry(0)

            messages.success(request, f"👋 Welcome back, {user.profile.name}!")
            return redirect("student_dashboard")
    else:
        form = StudentLoginForm()

    return render(request, "accounts/student_login.html", {"form": form})


def librarian_login(request):
    """Librarian-specific login view"""
    if request.user.is_authenticated:
        # Check if already logged in user is a librarian
        if hasattr(request.user, "profile") and request.user.profile.is_librarian:
            return redirect("librarian_dashboard")
        return redirect("home")

    if request.method == "POST":
        form = LibrarianLoginForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data["user"]
            remember_me = form.cleaned_data.get("remember_me", False)

            login(request, user)

            # Set session expiry
            if not remember_me:
                request.session.set_expiry(0)

            messages.success(request, f"👋 Welcome back, {user.profile.name}!")
            return redirect("librarian_dashboard")
    else:
        form = LibrarianLoginForm()

    return render(request, "accounts/librarian_login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect("login")


# ============= HELPER VIEWS =============

# @login_required
# def profile_view(request):
#     """Display user profile information"""
#     profile = request.user.profile

#     context = {
#         'profile': profile,
#         'user': request.user,
#     }

#     return render(request, "myapp/profile.html", context)


# @login_required
# def check_approval_status(request):
#     """AJAX endpoint to check user approval status"""
#     if hasattr(request.user, 'profile'):
#         profile = request.user.profile
#         return JsonResponse({
#             'status': profile.status,
#             'is_approved': profile.is_approved(),
#             'role': profile.role,
#         })

#     return JsonResponse({'error': 'Profile not found'}, status=404)


@login_required(login_url="librarian_login")
def librarian_dashboard(request):
    """Librarian dashboard showing library statistics and management options"""

    # Check if user has a profile
    if not hasattr(request.user, "profile"):
        messages.error(
            request,
            "❌ No profile found for your account. Please contact the administrator.",
        )
        return redirect("home")

    profile = request.user.profile

    # Check if user is a librarian
    if not profile.is_librarian:
        messages.warning(
            request, "⚠️ Access denied. This dashboard is only for librarians."
        )
        return redirect("home")

    # Check if librarian is approved
    if not profile.is_approved():
        messages.warning(
            request,
            "⏳ Your account is still pending approval. Please wait for admin approval.",
        )
        return redirect("home")

    # Get all students
    students = UserProfile.objects.filter(role="student", status="approved")

    # Get all books
    books = Book.objects.all()

    # Get active issued books
    active_issued = IssuedBook.objects.filter(is_returned=False).select_related(
        "book", "student", "student__user"
    )

    # Get all issued books
    all_issued = (
        IssuedBook.objects.all()
        .select_related("book", "student", "student__user")
        .order_by("-issue_date")
    )

    # Statistics
    total_books = books.count()
    total_students = students.count()
    total_active_borrowed = active_issued.count()
    total_returned = IssuedBook.objects.filter(is_returned=True).count()
    available_books = books.filter(quantity__gt=0).count()
    unavailable_books = books.filter(quantity=0).count()

    # Pending approvals
    pending_approvals = UserProfile.objects.filter(status="pending").count()

    # Recent activities
    recent_issued = (
        IssuedBook.objects.all()
        .select_related("book", "student")
        .order_by("-issue_date")[:10]
    )

    context = {
        "profile": profile,
        "librarian": profile,  # For backward compatibility
        "total_books": total_books,
        "total_students": total_students,
        "total_active_borrowed": total_active_borrowed,
        "total_returned": total_returned,
        "available_books": available_books,
        "unavailable_books": unavailable_books,
        "pending_approvals": pending_approvals,
        "recent_issued": recent_issued,
        "active_issued": active_issued,
        "all_issued": all_issued,
        "students": students,
        "books": books,
    }

    return render(request, "myapp/librarian_dashboard.html", context)


# @login_required(login_url="login")
# def admin_dashboard(request):
#     """Admin dashboard for user approval and system management"""
#     if not request.user.is_superuser:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     # Get pending approvals with pagination
#     pending_approvals = (
#         UserApproval.objects.filter(status="pending")
#         .select_related("user")
#         .order_by("-created_at")
#     )

#     pending_paginator = Paginator(pending_approvals, 10)
#     pending_page = request.GET.get("pending_page")
#     try:
#         pending_page_obj = pending_paginator.page(pending_page)
#     except PageNotAnInteger:
#         pending_page_obj = pending_paginator.page(1)
#     except EmptyPage:
#         pending_page_obj = pending_paginator.page(pending_paginator.num_pages)

#     # Get approved users with pagination
#     approved_users = (
#         UserApproval.objects.filter(status="approved")
#         .select_related("user")
#         .order_by("-approval_date")
#     )

#     approved_paginator = Paginator(approved_users, 10)
#     approved_page = request.GET.get("approved_page")
#     try:
#         approved_page_obj = approved_paginator.page(approved_page)
#     except PageNotAnInteger:
#         approved_page_obj = approved_paginator.page(1)
#     except EmptyPage:
#         approved_page_obj = approved_paginator.page(approved_paginator.num_pages)

#     # Get rejected users with pagination
#     rejected_users = (
#         UserApproval.objects.filter(status="rejected")
#         .select_related("user")
#         .order_by("-approval_date")
#     )

#     rejected_paginator = Paginator(rejected_users, 10)
#     rejected_page = request.GET.get("rejected_page")
#     try:
#         rejected_page_obj = rejected_paginator.page(rejected_page)
#     except PageNotAnInteger:
#         rejected_page_obj = rejected_paginator.page(1)
#     except EmptyPage:
#         rejected_page_obj = rejected_paginator.page(rejected_paginator.num_pages)

#     # Statistics
#     total_pending = pending_approvals.count()
#     total_approved = approved_users.count()
#     total_rejected = rejected_users.count()
#     total_librarians = UserApproval.objects.filter(
#         role="librarian", status="approved"
#     ).count()
#     total_students = UserApproval.objects.filter(
#         role="student", status="approved"
#     ).count()

#     context = {
#         "pending_approvals": pending_page_obj.object_list,
#         "pending_page_obj": pending_page_obj,
#         "approved_users": approved_page_obj.object_list,
#         "approved_page_obj": approved_page_obj,
#         "rejected_users": rejected_page_obj.object_list,
#         "rejected_page_obj": rejected_page_obj,
#         "total_pending": total_pending,
#         "total_approved": total_approved,
#         "total_rejected": total_rejected,
#         "total_librarians": total_librarians,
#         "total_students": total_students,
#     }
#     return render(request, "myapp/admin_dashboard.html", context)

# @login_required(login_url="login")
# def approve_user(request, user_id):
#     """Approve a pending user"""
#     if not request.user.is_superuser:
#         messages.error(request, "You do not have permission to perform this action!")
#         return redirect("myapp:home")

#     try:
#         user = User.objects.get(id=user_id)
#         approval = UserApproval.objects.get(user=user)

#         if approval.status != "pending":
#             messages.warning(request, "This user has already been processed!")
#             return redirect("myapp:admin_dashboard")

#         # Approve user
#         user.is_active = True
#         if approval.role == "librarian":
#             user.is_staff = True
#         user.save()

#         # Update approval record
#         approval.status = "approved"
#         approval.approved_by = request.user
#         approval.approval_date = timezone.now()
#         approval.save()

#         messages.success(
#             request, f"User '{user.username}' has been approved as {approval.role}!"
#         )
#     except User.DoesNotExist:
#         messages.error(request, "User not found!")
#     except UserApproval.DoesNotExist:
#         messages.error(request, "Approval record not found!")

#     return redirect("myapp:admin_dashboard")

# @login_required(login_url="login")
# def reject_user(request, user_id):
#     """Reject a pending user"""
#     if not request.user.is_superuser:
#         messages.error(request, "You do not have permission to perform this action!")
#         return redirect("myapp:home")

#     if request.method == "POST":
#         reason = request.POST.get("reason", "No reason provided")

#         try:
#             user = User.objects.get(id=user_id)
#             approval = UserApproval.objects.get(user=user)

#             if approval.status != "pending":
#                 messages.warning(request, "This user has already been processed!")
#                 return redirect("myapp:admin_dashboard")

#             # Reject user
#             approval.status = "rejected"
#             approval.approved_by = request.user
#             approval.rejection_reason = reason
#             approval.approval_date = timezone.now()
#             approval.rejection_date = timezone.now()
#             approval.save()

#             messages.success(
#                 request,
#                 f"User '{user.username}' has been rejected! Their account will be automatically deleted after 24 hours.",
#             )
#         except User.DoesNotExist:
#             messages.error(request, "User not found!")
#         except UserApproval.DoesNotExist:
#             messages.error(request, "Approval record not found!")

#         return redirect("myapp:admin_dashboard")

#     return render(request, "myapp/reject_user.html", {"user_id": user_id})


@login_required(login_url="login")
def student_dashboard(request):
    """Student dashboard showing borrowed books and library books"""

    # Check if user has a profile
    if not hasattr(request.user, "profile"):
        messages.error(
            request,
            "❌ No profile found for your account. Please contact the administrator.",
        )
        return redirect("home")

    profile = request.user.profile

    # Check if user is a student
    if not profile.is_student:
        messages.warning(
            request, "⚠️ Access denied. This dashboard is only for students."
        )
        return redirect("home")

    # Check if student is approved
    if not profile.is_approved():
        messages.warning(
            request,
            "⏳ Your account is still pending approval. Please wait for admin approval.",
        )
        return redirect("home")

    # Get student's borrowed books
    active_borrowed = (
        IssuedBook.objects.filter(student=profile, is_returned=False)
        .select_related("book")
        .order_by("-issue_date")
    )

    borrowed_history = (
        IssuedBook.objects.filter(student=profile)
        .select_related("book")
        .order_by("-issue_date")
    )

    # Get all books with search and filter
    books = Book.objects.all()

    # Get filter and search parameters
    filter_status = request.GET.get("status", "all")
    search_query = request.GET.get("search", "").strip()

    # Search functionality
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query)
            | Q(author__icontains=search_query)
            | Q(isbn__icontains=search_query)
        )

    # Filter by availability
    if filter_status == "available":
        books = books.filter(quantity__gt=0)
    elif filter_status == "unavailable":
        books = books.filter(quantity=0)

    # Order books by creation date (newest first)
    books = books.order_by("-created_at")

    # Count statistics
    current_borrowed_count = active_borrowed.count()
    total_borrowed_count = borrowed_history.count()
    returned_count = borrowed_history.filter(is_returned=True).count()
    available_books_count = Book.objects.filter(quantity__gt=0).count()

    # Calculate if student can borrow more books (e.g., limit to 5 active borrowed books)
    MAX_BORROWED_BOOKS = 5
    can_borrow_more = current_borrowed_count < MAX_BORROWED_BOOKS

    context = {
        "profile": profile,
        "student": profile,  # For backward compatibility
        "current_borrowed": active_borrowed,
        "borrowing_history": borrowed_history,
        "all_books": books,
        "filter_status": filter_status,
        "search_query": search_query,
        "current_borrowed_count": current_borrowed_count,
        "total_borrowed_count": total_borrowed_count,
        "returned_count": returned_count,
        "available_books_count": available_books_count,
        "can_borrow_more": can_borrow_more,
        "max_borrowed_books": MAX_BORROWED_BOOKS,
        "student_info": profile.get_full_info(),
    }

    return render(request, "accounts/student_dashboard.html", context)


# # ============= STUDENT VIEWS =============
# @login_required(login_url="myapp:login")
# def student_list(request):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     students = Student.objects.all()
#     search_query = request.GET.get("search", "")

#     # Search functionality
#     if search_query:
#         students = students.filter(
#             Q(name__icontains=search_query)
#             | Q(id_number__icontains=search_query)
#             | Q(department__icontains=search_query)
#         )

#     # Pagination
#     paginator = Paginator(students, 10)  # 10 students per page
#     page_number = request.GET.get("page")
#     try:
#         page_obj = paginator.page(page_number)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)

#     context = {
#         "students": page_obj.object_list,
#         "page_obj": page_obj,
#         "total_students": Student.objects.count(),
#         "search_query": search_query,
#     }
#     return render(request, "myapp/student_list.html", context)


# @login_required(login_url="myapp:login")
# def student_detail(request, pk):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     student = get_object_or_404(Student, pk=pk)
#     issued_books = student.issued_books.all()
#     active_issues = issued_books.filter(is_returned=False)

#     context = {
#         "student": student,
#         "issued_books": issued_books,
#         "active_issues": active_issues,
#         "total_borrowed": active_issues.count(),
#     }
#     return render(request, "myapp/student_detail.html", context)


# @login_required(login_url="myapp:login")
# def create_student(request):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     if request.method == "POST":
#         form = StudentForm(request.POST)
#         if form.is_valid():
#             student = form.save()
#             messages.success(request, f"Student '{student.name}' created successfully!")
#             return redirect("myapp:student_list")
#     else:
#         form = StudentForm()

#     context = {
#         "form": form,
#         "title": "Add New Student",
#         "button_text": "Create Student",
#     }
#     return render(request, "myapp/student_form.html", context)


# @login_required(login_url="myapp:login")
# def edit_student(request, pk):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     student = get_object_or_404(Student, pk=pk)

#     if request.method == "POST":
#         form = StudentForm(request.POST, instance=student)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f"Student '{student.name}' updated successfully!")
#             return redirect("myapp:student_detail", pk=student.pk)
#     else:
#         form = StudentForm(instance=student)

#     context = {
#         "form": form,
#         "student": student,
#         "title": f"Edit: {student.name}",
#         "button_text": "Update Student",
#     }
#     return render(request, "myapp/student_form.html", context)


# @login_required(login_url="myapp:login")
# def delete_student(request, pk):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     student = get_object_or_404(Student, pk=pk)

#     if request.method == "POST":
#         student_name = student.name
#         student.delete()
#         messages.success(request, f"Student '{student_name}' deleted successfully!")
#         return redirect("myapp:student_list")

#     context = {
#         "student": student,
#     }
#     return render(request, "myapp/student_confirm_delete.html", context)

