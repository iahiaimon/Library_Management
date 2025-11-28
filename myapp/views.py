from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Book, Student, IssuedBook, UserApproval, Librarian
from .forms import BookForm, StudentForm, IssuedBookForm, ReturnBookForm, RegistrationForm, StudentRegistrationForm, LibrarianRegistrationForm


# ============= AUTHENTICATION VIEWS =============
def register(request):
    if request.user.is_authenticated:
        return redirect('myapp:home')
    
    role = request.GET.get('role', 'student')  # Get role from URL parameter
    
    if request.method == 'POST':
        role = request.POST.get('role', 'student')
        
        if role == 'student':
            form = StudentRegistrationForm(request.POST)
        else:
            form = LibrarianRegistrationForm(request.POST)
        
        if form.is_valid():
            if role == 'student':
                # Student registration
                name = form.cleaned_data.get('name')
                email = form.cleaned_data.get('email')
                id_number = form.cleaned_data.get('id_number')
                department = form.cleaned_data.get('department')
                phone_number = form.cleaned_data.get('phone_number')
                password = form.cleaned_data.get('password1')
                
                # Use email as username (email is unique, so it works as identifier)
                user = User.objects.create_user(
                    username=email,  # Use email as username for uniqueness
                    email=email,
                    password=password,
                    is_active=False
                )
                
                # Create student profile
                Student.objects.create(
                    user=user,
                    name=name,
                    email=email,
                    id_number=id_number,
                    department=department,
                    phone_number=phone_number
                )
                
            else:
                # Librarian registration
                email = form.cleaned_data.get('email')
                phone_number = form.cleaned_data.get('phone_number')
                password = form.cleaned_data.get('password1')
                
                # Use email as username (email is unique, so it works as identifier)
                user = User.objects.create_user(
                    username=email,  # Use email as username for uniqueness
                    email=email,
                    password=password,
                    is_active=False
                )
                
                # Create librarian profile
                Librarian.objects.create(
                    user=user,
                    email=email,
                    phone_number=phone_number
                )
            
            # Create approval record
            UserApproval.objects.create(user=user, role=role)
            
            messages.success(request, "Account created successfully! Please wait for admin approval.")
            return redirect('myapp:login')
    else:
        if role == 'student':
            form = StudentRegistrationForm()
        else:
            form = LibrarianRegistrationForm()
    
    return render(request, 'myapp/register.html', {'form': form, 'role': role})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('myapp:home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # First, check if user exists with this email
        try:
            user = User.objects.get(username=email)
            
            # Check if password is correct
            if user.check_password(password):
                # Password is correct
                # Check if user is admin/superuser (they don't need approval)
                if user.is_superuser:
                    # Admin can login directly
                    login(request, user)
                    messages.success(request, "Welcome back!")
                    return redirect('myapp:home')
                
                # For regular users, check approval status
                try:
                    approval = UserApproval.objects.get(user=user)
                    
                    # Check approval status
                    if approval.status == 'pending':
                        messages.warning(
                            request, 
                            "⏳ Your registration request is still PENDING! ⏳ Please wait for admin approval."
                        )
                        return redirect('myapp:login')
                    elif approval.status == 'rejected':
                        messages.error(
                            request, 
                            f"❌ Your registration request has been rejected. Reason: {approval.rejection_reason if approval.rejection_reason else 'Not specified'} ❌ You can reapply after 24 hours."
                        )
                        return redirect('myapp:login')
                    elif approval.status == 'approved':
                        # Approved, now check if account is active
                        if user.is_active:
                            # All good, login the user
                            login(request, user)
                            messages.success(request, "Welcome back!")
                            return redirect('myapp:home')
                        else:
                            messages.error(request, "Your account has been deactivated. Please contact the administrator.")
                            return redirect('myapp:login')
                    else:
                        messages.error(request, "Your account status is unknown. Please contact the administrator.")
                        return redirect('myapp:login')
                        
                except UserApproval.DoesNotExist:
                    # User exists but no approval record found
                    messages.error(request, "Your account is not registered properly. Please contact the administrator.")
                    return redirect('myapp:login')
            else:
                # Password is incorrect
                messages.error(request, "Invalid email or password!")
        except User.DoesNotExist:
            # User does not exist
            messages.error(request, "Invalid email or password!")
    
    return render(request, 'myapp/login.html')


def logout_view(request):
    logout(request)
    # Clear all messages and add only logout message
    from django.contrib.messages import get_messages
    storage = get_messages(request)
    for _ in storage:
        pass  # Iterate through to clear all messages
    storage.used = True
    
    messages.success(request, "You have been logged out successfully!")
    return redirect('myapp:login')


@login_required(login_url='myapp:login')
@login_required(login_url='myapp:login')
def home(request):
    """Dashboard that redirects based on user role"""
    # Check if user is superuser (admin)
    if request.user.is_superuser:
        return redirect('myapp:admin_dashboard')
    elif request.user.is_staff:
        return redirect('myapp:librarian_dashboard')
    else:
        return redirect('myapp:student_dashboard')


@login_required(login_url='myapp:login')
def librarian_dashboard(request):
    """Librarian/Admin dashboard with statistics"""
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    # Statistics - only count approved students
    approved_student_ids = UserApproval.objects.filter(
        role='student', 
        status='approved'
    ).values_list('user_id', flat=True)
    
    total_books = Book.objects.count()
    total_students = Student.objects.filter(user_id__in=approved_student_ids).count()
    available_books = Book.objects.filter(quantity__gt=0).count()
    active_issues = IssuedBook.objects.filter(is_returned=False).count()
    
    # Recent activities
    recent_issues = IssuedBook.objects.select_related('student', 'book').order_by('-issue_date')[:5]
    
    context = {
        'total_books': total_books,
        'total_students': total_students,
        'available_books': available_books,
        'active_issues': active_issues,
        'recent_issues': recent_issues,
    }
    return render(request, 'myapp/librarian_dashboard.html', context)


@login_required(login_url='myapp:login')
def admin_dashboard(request):
    """Admin dashboard for user approval and system management"""
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    # Get pending approvals with pagination
    pending_approvals = UserApproval.objects.filter(status='pending').select_related('user').order_by('-created_at')
    
    pending_paginator = Paginator(pending_approvals, 10)
    pending_page = request.GET.get('pending_page')
    try:
        pending_page_obj = pending_paginator.page(pending_page)
    except PageNotAnInteger:
        pending_page_obj = pending_paginator.page(1)
    except EmptyPage:
        pending_page_obj = pending_paginator.page(pending_paginator.num_pages)
    
    # Get approved users with pagination
    approved_users = UserApproval.objects.filter(status='approved').select_related('user').order_by('-approval_date')
    
    approved_paginator = Paginator(approved_users, 10)
    approved_page = request.GET.get('approved_page')
    try:
        approved_page_obj = approved_paginator.page(approved_page)
    except PageNotAnInteger:
        approved_page_obj = approved_paginator.page(1)
    except EmptyPage:
        approved_page_obj = approved_paginator.page(approved_paginator.num_pages)
    
    # Get rejected users with pagination
    rejected_users = UserApproval.objects.filter(status='rejected').select_related('user').order_by('-approval_date')
    
    rejected_paginator = Paginator(rejected_users, 10)
    rejected_page = request.GET.get('rejected_page')
    try:
        rejected_page_obj = rejected_paginator.page(rejected_page)
    except PageNotAnInteger:
        rejected_page_obj = rejected_paginator.page(1)
    except EmptyPage:
        rejected_page_obj = rejected_paginator.page(rejected_paginator.num_pages)
    
    # Statistics
    total_pending = pending_approvals.count()
    total_approved = approved_users.count()
    total_rejected = rejected_users.count()
    total_librarians = UserApproval.objects.filter(role='librarian', status='approved').count()
    total_students = UserApproval.objects.filter(role='student', status='approved').count()
    
    context = {
        'pending_approvals': pending_page_obj.object_list,
        'pending_page_obj': pending_page_obj,
        'approved_users': approved_page_obj.object_list,
        'approved_page_obj': approved_page_obj,
        'rejected_users': rejected_page_obj.object_list,
        'rejected_page_obj': rejected_page_obj,
        'total_pending': total_pending,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
        'total_librarians': total_librarians,
        'total_students': total_students,
    }
    return render(request, 'myapp/admin_dashboard.html', context)


@login_required(login_url='myapp:login')
def approve_user(request, user_id):
    """Approve a pending user"""
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to perform this action!")
        return redirect('myapp:home')
    
    try:
        user = User.objects.get(id=user_id)
        approval = UserApproval.objects.get(user=user)
        
        if approval.status != 'pending':
            messages.warning(request, "This user has already been processed!")
            return redirect('myapp:admin_dashboard')
        
        # Approve user
        user.is_active = True
        if approval.role == 'librarian':
            user.is_staff = True
        user.save()
        
        # Update approval record
        approval.status = 'approved'
        approval.approved_by = request.user
        approval.approval_date = timezone.now()
        approval.save()
        
        messages.success(request, f"User '{user.username}' has been approved as {approval.role}!")
    except User.DoesNotExist:
        messages.error(request, "User not found!")
    except UserApproval.DoesNotExist:
        messages.error(request, "Approval record not found!")
    
    return redirect('myapp:admin_dashboard')


@login_required(login_url='myapp:login')
def reject_user(request, user_id):
    """Reject a pending user"""
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to perform this action!")
        return redirect('myapp:home')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'No reason provided')
        
        try:
            user = User.objects.get(id=user_id)
            approval = UserApproval.objects.get(user=user)
            
            if approval.status != 'pending':
                messages.warning(request, "This user has already been processed!")
                return redirect('myapp:admin_dashboard')
            
            # Reject user
            approval.status = 'rejected'
            approval.approved_by = request.user
            approval.rejection_reason = reason
            approval.approval_date = timezone.now()
            approval.rejection_date = timezone.now()
            approval.save()
            
            messages.success(request, f"User '{user.username}' has been rejected! Their account will be automatically deleted after 24 hours.")
        except User.DoesNotExist:
            messages.error(request, "User not found!")
        except UserApproval.DoesNotExist:
            messages.error(request, "Approval record not found!")
        
        return redirect('myapp:admin_dashboard')
    
    return render(request, 'myapp/reject_user.html', {'user_id': user_id})


@login_required(login_url='myapp:login')
def student_dashboard(request):
    """Student dashboard showing borrowed books and library books"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.info(request, "No student profile found for your account. Please contact the librarian.")
        student = None
    
    # Get student's borrowed books
    active_borrowed = []
    borrowed_history = []
    
    if student:
        active_borrowed = student.issued_books.filter(is_returned=False)
        borrowed_history = student.issued_books.all()
    
    # Get all books with search and filter
    books = Book.objects.all()
    filter_status = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Search functionality
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Filter by availability
    if filter_status == 'available':
        books = books.filter(quantity__gt=0)
    elif filter_status == 'unavailable':
        books = books.filter(quantity=0)
    
    # Count statistics
    current_borrowed_count = active_borrowed.count() if student else 0
    total_borrowed_count = borrowed_history.count() if student else 0
    
    context = {
        'student': student,
        'current_borrowed': active_borrowed,
        'borrowing_history': borrowed_history,
        'all_books': books,
        'filter_status': filter_status,
        'search_query': search_query,
        'current_borrowed_count': current_borrowed_count,
        'total_borrowed_count': total_borrowed_count,
    }
    return render(request, 'myapp/student_dashboard.html', context)


# ============= BOOK VIEWS =============
@login_required(login_url='myapp:login')
def book_list(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    books = Book.objects.all()
    search_query = request.GET.get('search', '')
    filter_status = request.GET.get('status', 'all')
    
    # Search functionality
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Filter by availability
    if filter_status == 'available':
        books = books.filter(quantity__gt=0)
    elif filter_status == 'unavailable':
        books = books.filter(quantity=0)
    
    # Pagination
    paginator = Paginator(books, 10)  # 10 books per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'books': page_obj.object_list,
        'page_obj': page_obj,
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(quantity__gt=0).count(),
        'search_query': search_query,
        'filter_status': filter_status,
    }
    return render(request, 'myapp/book_list.html', context)


@login_required(login_url='myapp:login')
def create_book(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Book '{form.cleaned_data['title']}' created successfully!")
            return redirect('myapp:book_list')
    else:
        form = BookForm()
    
    context = {
        'form': form,
        'title': 'Add New Book',
        'button_text': 'Create Book'
    }
    return render(request, 'myapp/book_form.html', context)


@login_required(login_url='myapp:login')
def edit_book(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"Book '{form.cleaned_data['title']}' updated successfully!")
            return redirect('myapp:book_list')
    else:
        form = BookForm(instance=book)
    
    context = {
        'form': form,
        'book': book,
        'title': f'Edit: {book.title}',
        'button_text': 'Update Book'
    }
    return render(request, 'myapp/book_form.html', context)


@login_required(login_url='myapp:login')
def delete_book(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f"Book '{book_title}' deleted successfully!")
        return redirect('myapp:book_list')
    
    context = {
        'book': book,
    }
    return render(request, 'myapp/book_confirm_delete.html', context)


# ============= STUDENT VIEWS =============
@login_required(login_url='myapp:login')
def student_list(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    students = Student.objects.all()
    search_query = request.GET.get('search', '')
    
    # Search functionality
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(id_number__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(students, 10)  # 10 students per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'students': page_obj.object_list,
        'page_obj': page_obj,
        'total_students': Student.objects.count(),
        'search_query': search_query,
    }
    return render(request, 'myapp/student_list.html', context)


@login_required(login_url='myapp:login')
def student_detail(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    student = get_object_or_404(Student, pk=pk)
    issued_books = student.issued_books.all()
    active_issues = issued_books.filter(is_returned=False)
    
    context = {
        'student': student,
        'issued_books': issued_books,
        'active_issues': active_issues,
        'total_borrowed': active_issues.count(),
    }
    return render(request, 'myapp/student_detail.html', context)


@login_required(login_url='myapp:login')
def create_student(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.name}' created successfully!")
            return redirect('myapp:student_list')
    else:
        form = StudentForm()
    
    context = {
        'form': form,
        'title': 'Add New Student',
        'button_text': 'Create Student'
    }
    return render(request, 'myapp/student_form.html', context)


@login_required(login_url='myapp:login')
def edit_student(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student '{student.name}' updated successfully!")
            return redirect('myapp:student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
        'title': f'Edit: {student.name}',
        'button_text': 'Update Student'
    }
    return render(request, 'myapp/student_form.html', context)


@login_required(login_url='myapp:login')
def delete_student(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student_name = student.name
        student.delete()
        messages.success(request, f"Student '{student_name}' deleted successfully!")
        return redirect('myapp:student_list')
    
    context = {
        'student': student,
    }
    return render(request, 'myapp/student_confirm_delete.html', context)


# ============= ISSUE/RETURN VIEWS =============
@login_required(login_url='myapp:login')
def issued_books_list(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    issued_books = IssuedBook.objects.select_related('student', 'book').all()
    active_issues = issued_books.filter(is_returned=False)
    returned_books = issued_books.filter(is_returned=True)
    
    # Filter by status if provided
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'active':
        issued_books = active_issues
    elif status_filter == 'returned':
        issued_books = returned_books
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        issued_books = issued_books.filter(
            Q(student__name__icontains=search_query) |
            Q(student__id_number__icontains=search_query) |
            Q(book__title__icontains=search_query)
        )
    
    # Order by issue date descending
    issued_books = issued_books.order_by('-issue_date')
    
    # Pagination
    paginator = Paginator(issued_books, 15)  # 15 issues per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'issued_books': page_obj.object_list,
        'page_obj': page_obj,
        'total_issued': IssuedBook.objects.filter(is_returned=False).count(),
        'total_returned': IssuedBook.objects.filter(is_returned=True).count(),
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'myapp/issued_books_list.html', context)


@login_required(login_url='myapp:login')
def issue_book(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    if request.method == 'POST':
        form = IssuedBookForm(request.POST)
        if form.is_valid():
            issued_book = form.save()
            # Reduce book quantity
            book = issued_book.book
            book.quantity -= issued_book.quantity
            book.save()
            
            messages.success(
                request,
                f"Book '{book.title}' issued to '{issued_book.student.name}' ({issued_book.quantity} copies)"
            )
            return redirect('myapp:issued_books_list')
    else:
        form = IssuedBookForm()
    
    context = {
        'form': form,
        'title': 'Issue Book',
        'button_text': 'Issue Book'
    }
    return render(request, 'myapp/issue_book_form.html', context)


@login_required(login_url='myapp:login')
def return_book(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page!")
        return redirect('myapp:home')
    
    issued_book = get_object_or_404(IssuedBook, pk=pk)
    
    if issued_book.is_returned:
        messages.warning(request, "This book has already been returned!")
        return redirect('myapp:issued_books_list')
    
    if request.method == 'POST':
        form = ReturnBookForm(request.POST, instance=issued_book)
        if form.is_valid():
            quantity_returned = form.cleaned_data['quantity']
            
            if quantity_returned > issued_book.quantity:
                messages.error(request, f"Cannot return more than {issued_book.quantity} copies!")
                return render(request, 'myapp/return_book_form.html', {'form': form, 'issued_book': issued_book})
            
            # Update issued book
            issued_book.quantity -= quantity_returned
            issued_book.return_date = None  # Will be set when fully returned
            
            # If all copies returned, mark as returned
            if issued_book.quantity == 0:
                issued_book.is_returned = True
                issued_book.return_date = timezone.now().date()
            
            issued_book.save()
            
            # Increase book quantity
            book = issued_book.book
            book.quantity += quantity_returned
            book.save()
            
            messages.success(
                request,
                f"'{quantity_returned}' copy/copies of '{book.title}' returned successfully!"
            )
            return redirect('myapp:issued_books_list')
    else:
        form = ReturnBookForm(instance=issued_book)
    
    context = {
        'form': form,
        'issued_book': issued_book,
    }
    return render(request, 'myapp/return_book_form.html', context)
