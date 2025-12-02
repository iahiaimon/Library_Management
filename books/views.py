from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserProfile, Book, IssuedBook
from .forms import BookForm, IssuedBookForm, ReturnBookForm
from .models import UserProfile

# Create your views here.


@login_required(login_url="login")
def home(request):
    """Home page that redirects based on user role"""
    try:
        profile = request.user
    except AttributeError:
        messages.info(
            request, "👋 Welcome! Please complete your profile to access the system."
        )
        return redirect("profile_view")

    # Check approval status
    if not profile.is_approved():
        if profile.is_pending():
            messages.warning(
                request,
                "⏳ Your account is pending approval. Please wait for administrator review.",
            )
        elif profile.is_rejected():
            messages.error(
                request,
                f"❌ Your account was rejected. Reason: {profile.rejection_reason or 'Not specified'}",
            )
        return redirect("login")

    # Redirect based on role
    if profile.is_student:
        return redirect("student_dashboard")
    elif profile.is_librarian:
        return redirect("librarian_dashboard")
    else:
        messages.error(request, "❌ Unknown user role. Please contact administrator.")
        return redirect("login")


# # ============= BOOK VIEWS =============
# @login_required(login_url="myapp:login")
# def book_list(request):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     books = Book.objects.all()
#     search_query = request.GET.get("search", "")
#     filter_status = request.GET.get("status", "all")

#     # Search functionality
#     if search_query:
#         books = books.filter(
#             Q(title__icontains=search_query)
#             | Q(author__icontains=search_query)
#             | Q(isbn__icontains=search_query)
#         )

#     # Filter by availability
#     if filter_status == "available":
#         books = books.filter(quantity__gt=0)
#     elif filter_status == "unavailable":
#         books = books.filter(quantity=0)

#     # Pagination
#     paginator = Paginator(books, 10)  # 10 books per page
#     page_number = request.GET.get("page")
#     try:
#         page_obj = paginator.page(page_number)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)

#     context = {
#         "books": page_obj.object_list,
#         "page_obj": page_obj,
#         "total_books": Book.objects.count(),
#         "available_books": Book.objects.filter(quantity__gt=0).count(),
#         "search_query": search_query,
#         "filter_status": filter_status,
#     }
#     return render(request, "myapp/book_list.html", context)


# @login_required(login_url="myapp:login")
# def create_book(request):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     if request.method == "POST":
#         form = BookForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request, f"Book '{form.cleaned_data['title']}' created successfully!"
#             )
#             return redirect("myapp:book_list")
#     else:
#         form = BookForm()

#     context = {"form": form, "title": "Add New Book", "button_text": "Create Book"}
#     return render(request, "myapp/book_form.html", context)


# @login_required(login_url="myapp:login")
# def edit_book(request, pk):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     book = get_object_or_404(Book, pk=pk)

#     if request.method == "POST":
#         form = BookForm(request.POST, request.FILES, instance=book)
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request, f"Book '{form.cleaned_data['title']}' updated successfully!"
#             )
#             return redirect("myapp:book_list")
#     else:
#         form = BookForm(instance=book)

#     context = {
#         "form": form,
#         "book": book,
#         "title": f"Edit: {book.title}",
#         "button_text": "Update Book",
#     }
#     return render(request, "myapp/book_form.html", context)


# @login_required(login_url="myapp:login")
# def delete_book(request, pk):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     book = get_object_or_404(Book, pk=pk)

#     if request.method == "POST":
#         book_title = book.title
#         book.delete()
#         messages.success(request, f"Book '{book_title}' deleted successfully!")
#         return redirect("myapp:book_list")

#     context = {
#         "book": book,
#     }
#     return render(request, "myapp/book_confirm_delete.html", context)


# # ============= ISSUE/RETURN VIEWS =============
# @login_required(login_url="myapp:login")
# def issued_books_list(request):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     issued_books = IssuedBook.objects.select_related("student", "book").all()
#     active_issues = issued_books.filter(is_returned=False)
#     returned_books = issued_books.filter(is_returned=True)

#     # Filter by status if provided
#     status_filter = request.GET.get("status", "all")
#     if status_filter == "active":
#         issued_books = active_issues
#     elif status_filter == "returned":
#         issued_books = returned_books

#     # Search functionality
#     search_query = request.GET.get("search", "")
#     if search_query:
#         issued_books = issued_books.filter(
#             Q(student__name__icontains=search_query)
#             | Q(student__id_number__icontains=search_query)
#             | Q(book__title__icontains=search_query)
#         )

#     # Order by issue date descending
#     issued_books = issued_books.order_by("-issue_date")

#     # Pagination
#     paginator = Paginator(issued_books, 15)  # 15 issues per page
#     page_number = request.GET.get("page")
#     try:
#         page_obj = paginator.page(page_number)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)

#     context = {
#         "issued_books": page_obj.object_list,
#         "page_obj": page_obj,
#         "total_issued": IssuedBook.objects.filter(is_returned=False).count(),
#         "total_returned": IssuedBook.objects.filter(is_returned=True).count(),
#         "status_filter": status_filter,
#         "search_query": search_query,
#     }
#     return render(request, "myapp/issued_books_list.html", context)


# @login_required(login_url="myapp:login")
# def issue_book(request):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     if request.method == "POST":
#         form = IssuedBookForm(request.POST)
#         if form.is_valid():
#             issued_book = form.save()
#             # Reduce book quantity
#             book = issued_book.book
#             book.quantity -= issued_book.quantity
#             book.save()

#             messages.success(
#                 request,
#                 f"Book '{book.title}' issued to '{issued_book.student.name}' ({issued_book.quantity} copies)",
#             )
#             return redirect("myapp:issued_books_list")
#     else:
#         form = IssuedBookForm()

#     context = {"form": form, "title": "Issue Book", "button_text": "Issue Book"}
#     return render(request, "myapp/issue_book_form.html", context)


# @login_required(login_url="myapp:login")
# def return_book(request, pk):
#     if not request.user.is_staff:
#         messages.error(request, "You do not have permission to access this page!")
#         return redirect("myapp:home")

#     issued_book = get_object_or_404(IssuedBook, pk=pk)

#     if issued_book.is_returned:
#         messages.warning(request, "This book has already been returned!")
#         return redirect("myapp:issued_books_list")

#     if request.method == "POST":
#         form = ReturnBookForm(request.POST, instance=issued_book)
#         if form.is_valid():
#             quantity_returned = form.cleaned_data["quantity"]

#             if quantity_returned > issued_book.quantity:
#                 messages.error(
#                     request, f"Cannot return more than {issued_book.quantity} copies!"
#                 )
#                 return render(
#                     request,
#                     "myapp/return_book_form.html",
#                     {"form": form, "issued_book": issued_book},
#                 )

#             # Update issued book
#             issued_book.quantity -= quantity_returned
#             issued_book.return_date = None  # Will be set when fully returned

#             # If all copies returned, mark as returned
#             if issued_book.quantity == 0:
#                 issued_book.is_returned = True
#                 issued_book.return_date = timezone.now().date()

#             issued_book.save()

#             # Increase book quantity
#             book = issued_book.book
#             book.quantity += quantity_returned
#             book.save()

#             messages.success(
#                 request,
#                 f"'{quantity_returned}' copy/copies of '{book.title}' returned successfully!",
#             )
#             return redirect("myapp:issued_books_list")
#     else:
#         form = ReturnBookForm(instance=issued_book)

#     context = {
#         "form": form,
#         "issued_book": issued_book,
#     }
#     return render(request, "myapp/return_book_form.html", context)
