from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify
import uuid
from sports.models import Sport,Position


class UserManager(BaseUserManager):
    """Custom user manager to create users and superusers."""


    def create_superuser(self, email, password=None, **extra_fields):
        """Ensure superadmins have correct flags and a username."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superadmin")

        return self.create_user(email, password, **extra_fields)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        if not extra_fields.get("username"):
            base_username = slugify(email.split("@")[0])
            unique_suffix = uuid.uuid4().hex[:6]
            extra_fields["username"] = f"{base_username}-{unique_suffix}"

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superadmin")
        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    ROLE_CHOICES = [
        ("athlete", "Athlete"),
        ("coach", "Coach"),
        ("college_admin", "College Admin"),
        ("superadmin", "Superadmin"),
        ("general_user", "General User"),
    ]

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="athlete")
    first_name = models.CharField(max_length=30, blank=True, null=True)  
    middle_name = models.CharField(max_length=30, blank=True, null=True) 
    mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True)  
    last_name = models.CharField(max_length=30, blank=True, null=True) 
    profile_picture = models.TextField(null=True, blank=True)

 
    gender = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)  # Date of birth
    gender = models.CharField(max_length=10, null=True, blank=True)  # Gender (already there, just listed for clarity)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Height (e.g., in meters)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  #


    high_school = models.CharField(max_length=255, null=True, blank=True)
    college = models.CharField(max_length=255, null=True, blank=True)
    division = models.CharField(max_length=50, null=True, blank=True)
    school_year = models.CharField(max_length=50, null=True, blank=True)
    year_left_to_play = models.CharField(max_length=10, null=True, blank=True)

    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"
    

