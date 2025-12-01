from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile


class BaseRegistrationForm(forms.Form):
    """Base form with common registration fields"""

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "class": "form-control",
                "autocomplete": "email",
            }
        ),
    )

    name = forms.CharField(
        max_length=200,
        label="Full Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your full name",
                "class": "form-control",
            }
        ),
    )

    phone_number = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your phone number",
                "class": "form-control",
            }
        ),
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter a strong password (min 8 characters)",
                "class": "form-control",
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm your password",
                "class": "form-control",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered. Please use another.")
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered. Please use another.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")

        # Additional password strength validation
        if password1.isdigit():
            raise forms.ValidationError("Password cannot be entirely numeric.")
        if password1.isalpha():
            raise forms.ValidationError("Password must contain at least one number.")

        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match. Please try again.")

        return cleaned_data

class StudentRegistrationForm(BaseRegistrationForm):
    """Student registration form with student-specific fields"""

    id_number = forms.CharField(
        max_length=20,
        label="Student ID Number",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your student ID",
                "class": "form-control",
            }
        ),
    )

    department = forms.ChoiceField(
        label="Department",
        choices=UserProfile.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean_id_number(self):
        id_number = self.cleaned_data.get("id_number")
        if UserProfile.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError(
                "ID Number already registered. Please contact admin if this is an error."
            )
        return id_number

    def save(self):
        """Create User and UserProfile for student"""
        email = self.cleaned_data["email"]
        name = self.cleaned_data["name"]
        password = self.cleaned_data["password1"]

        # Create username from email
        username = email.split("@")[0]

        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name.split()[0] if name else "",
            last_name=" ".join(name.split()[1:]) if len(name.split()) > 1 else "",
        )

        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            role="student",
            name=name,
            email=email,
            phone_number=self.cleaned_data["phone_number"],
            id_number=self.cleaned_data["id_number"],
            department=self.cleaned_data["department"],
            status="pending",  # Awaiting approval
        )

        return user, profile

class LibrarianRegistrationForm(BaseRegistrationForm):
    """Librarian registration form without student-specific fields"""

    def save(self):
        """Create User and UserProfile for librarian"""
        email = self.cleaned_data["email"]
        name = self.cleaned_data["name"]
        password = self.cleaned_data["password1"]

        # Create username from email
        username = email.split("@")[0]

        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name.split()[0] if name else "",
            last_name=" ".join(name.split()[1:]) if len(name.split()) > 1 else "",
        )

        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            role="librarian",
            name=name,
            email=email,
            phone_number=self.cleaned_data["phone_number"],
            status="pending",  # Awaiting approval
        )

        return user, profile

class LoginForm(forms.Form):
    """Universal login form for both students and librarians"""

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "class": "form-control",
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "form-control",
                "autocomplete": "current-password",
            }
        ),
    )

    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Remember me",
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError("Invalid email or password.")

                # Check if user has a profile
                if not hasattr(user, "profile"):
                    raise forms.ValidationError(
                        "User profile not found. Please contact admin."
                    )

                # Check if user is approved
                if user.profile.status == "pending":
                    raise forms.ValidationError(
                        "Your account is pending approval. Please wait for admin approval."
                    )
                elif user.profile.status == "rejected":
                    raise forms.ValidationError(
                        "Your account has been rejected. Please contact admin for more information."
                    )

                cleaned_data["user"] = user

            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")

        return cleaned_data

class StudentLoginForm(LoginForm):
    """Student-specific login form with role validation"""

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")

        if user and hasattr(user, "profile"):
            if user.profile.role != "student":
                raise forms.ValidationError(
                    "This account is not registered as a student. Please use the librarian login."
                )

        return cleaned_data


class LibrarianLoginForm(LoginForm):
    """Librarian-specific login form with role validation"""

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")

        if user and hasattr(user, "profile"):
            if user.profile.role != "librarian":
                raise forms.ValidationError(
                    "This account is not registered as a librarian. Please use the student login."
                )

        return cleaned_data


class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile information"""

    class Meta:
        model = UserProfile
        fields = ["name", "phone_number", "id_number", "department"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your full name",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your phone number",
                }
            ),
            "id_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your student ID",
                    "readonly": True,  # ID number should not be editable
                }
            ),
            "department": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make student-specific fields optional if user is librarian
        if self.instance and self.instance.role == "librarian":
            self.fields["id_number"].required = False
            self.fields["department"].required = False
            self.fields["id_number"].widget = forms.HiddenInput()
            self.fields["department"].widget = forms.HiddenInput()
        else:
            # For students, make ID number read-only
            self.fields["id_number"].disabled = True


# class BookForm(forms.ModelForm):
#     class Meta:
#         model = Book
#         fields = ["title", "author", "isbn", "quantity", "cover_image"]
#         widgets = {
#             "title": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter book title",
#                     "required": True,
#                 }
#             ),
#             "author": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter author name",
#                     "required": True,
#                 }
#             ),
#             "isbn": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter ISBN (13 characters)",
#                     "maxlength": "13",
#                     "required": True,
#                 }
#             ),
#             "quantity": forms.NumberInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter quantity",
#                     "min": "0",
#                     "required": True,
#                 }
#             ),
#             "cover_image": forms.FileInput(
#                 attrs={
#                     "class": "form-control",
#                     "accept": "image/*",
#                     "placeholder": "Upload book cover image",
#                 }
#             ),
#         }
#         labels = {
#             "title": "Book Title",
#             "author": "Author Name",
#             "isbn": "ISBN",
#             "quantity": "Quantity",
#             "cover_image": "Book Cover Image",
#         }


# class IssuedBookForm(forms.ModelForm):
#     class Meta:
#         model = IssuedBook
#         fields = ["student", "book", "quantity"]
#         widgets = {
#             "student": forms.Select(attrs={"class": "form-control", "required": True}),
#             "book": forms.Select(attrs={"class": "form-control", "required": True}),
#             "quantity": forms.NumberInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter quantity",
#                     "min": "1",
#                     "required": True,
#                 }
#             ),
#         }
#         labels = {
#             "student": "Select Student",
#             "book": "Select Book",
#             "quantity": "Quantity to Issue",
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         book = cleaned_data.get("book")
#         quantity = cleaned_data.get("quantity")

#         if book and quantity and quantity > book.quantity:
#             raise forms.ValidationError(
#                 f"Not enough books available. Available: {book.quantity}"
#             )
#         return cleaned_data


# class ReturnBookForm(forms.ModelForm):
#     class Meta:
#         model = IssuedBook
#         fields = ["quantity"]
#         widgets = {
#             "quantity": forms.NumberInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter quantity to return",
#                     "min": "1",
#                     "required": True,
#                 }
#             ),
#         }
#         labels = {
#             "quantity": "Quantity to Return",
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         quantity = cleaned_data.get("quantity")
#         # quantity validation will be done in the view
#         return cleaned_data
