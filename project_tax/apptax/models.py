from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from cloudinary.models import CloudinaryField
from datetime import date 
from decimal import Decimal, InvalidOperation
import uuid
from django.core.validators import EmailValidator, RegexValidator

PAN_REGEX = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Apply the email validator
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    
    date_of_birth = models.DateField(null=True, blank=True)  # Optional field
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)  # Optional field
    
    # Apply PAN number validation using RegexValidator
    pan_number = models.CharField(
        max_length=10, 
        default='0000 0000', 
        null=True, 
        blank=True, 
        validators=[RegexValidator(regex=PAN_REGEX, message="Invalid PAN number format")]
    )
    
    address = models.TextField(null=True, blank=True)  # Optional field
    city = models.CharField(max_length=50, null=True, blank=True)  # Optional field
    state = models.CharField(max_length=50, null=True, blank=True)  # Optional field
    postal_code = models.CharField(max_length=10, null=True, blank=True)  # Optional field
    occupation = models.CharField(max_length=100, null=True, blank=True)  # Optional field
    annual_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional field
    taxpayer_status = models.CharField(max_length=50, null=True, blank=True)  # Optional field
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    profile_image = CloudinaryField('profile_image', null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Remove other fields from required

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age
        return None

from django.utils import timezone

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Check if the OTP is still valid (e.g., valid for 5 minutes)
        return (timezone.now() - self.created_at).total_seconds() < 300
    
class Contact(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, default='Anonymous')
    location = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name
    
from django.conf import settings  # Import settings to reference the CustomUser model

from cloudinary.models import CloudinaryField


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('PAN', 'PAN Card'),
        ('TAX', 'Tax Paid Slip'),
        ('SALARY', 'Salary Slip'),
        ('OTHER', 'Other Document'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_file = CloudinaryField('document')
    verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'document_type')

    def __str__(self):
        return f"{self.user.email} - {self.document_type}"

import uuid
from decimal import Decimal
from django.db import models
from datetime import date

class BasicTaxDetail(models.Model):
    entry_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Unique ID for each set of entries
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    financial_year = models.CharField(max_length=9)  # Example: 2024-25
    age = models.IntegerField()  # Storing age as an integer

    def save(self, *args, **kwargs):
        # Calculate age based on the user's date_of_birth
        if self.user.date_of_birth:
            today = date.today()
            self.age = today.year - self.user.date_of_birth.year - ((today.month, today.day) < (self.user.date_of_birth.month, self.user.date_of_birth.day))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.financial_year}"


class IncomeDetails(models.Model):
    entry_id = models.OneToOneField(BasicTaxDetail, on_delete=models.CASCADE, related_name="income_details",unique=True)  # Link to BasicTaxDetail
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    # Income fields
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    special_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    lta = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    other_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)

    # Exemptions
    hra_exempted = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    lta_exempted = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)

    # Other income sources
    income_from_interest = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    rental_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    interest_on_home_loan_self_occupied = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    interest_on_home_loan_let_out = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    income_from_digital_assets = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    other_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_gross_income(self):
        total_income = (
            self.basic_salary + self.hra + self.special_allowance +
            self.lta + self.other_allowance + self.income_from_interest +
            self.rental_income + self.income_from_digital_assets + self.other_income
        )
        exemptions = self.hra_exempted + self.lta_exempted
        return total_income - exemptions


class Deductions(models.Model):
    entry_id = models.OneToOneField(BasicTaxDetail, on_delete=models.CASCADE, related_name="deductions",unique=True)  # Link to BasicTaxDetail
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    section_80C = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    section_80D = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    section_80G = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    section_80E = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    section_80TTA = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    standard_deduction_old = models.DecimalField(max_digits=12, decimal_places=2, default=50000)
    standard_deduction_new = models.DecimalField(max_digits=12, decimal_places=2, default=75000)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_deductions_old(self):
        return self.section_80C + self.section_80D + self.section_80G + self.section_80E + self.section_80TTA + self.standard_deduction_old

    def calculate_total_deductions_new(self):
        return self.section_80D + self.section_80E + self.section_80TTA + self.standard_deduction_new

import logging
logger = logging.getLogger(__name__)

def is_valid_number(value):
    """Checks if the given value can be converted to a number."""
    try:
        # Try to convert the value to a float and check if it is a valid number
        float(value)
        return True
    except ValueError:
        return False


class TaxCalculation(models.Model):
    entry_id = models.OneToOneField(BasicTaxDetail, on_delete=models.CASCADE, related_name="tax_calculation", unique=True)  # Link to BasicTaxDetail
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    gross_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0.00))
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0.00))
    taxable_income_old_regime = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0.00))
    taxable_income_new_regime = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0.00))
    tax_old_regime = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0.00))
    tax_new_regime = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0.00))

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedbacks')
    calculation_type = models.CharField(max_length=100)  # Type of calculation (e.g., income tax, deduction)
    feedback_text = models.TextField()  # User's feedback on the calculation
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.calculation_type} Feedback"

    class Meta:
        ordering = ['-created_at']  # Show the latest feedback first