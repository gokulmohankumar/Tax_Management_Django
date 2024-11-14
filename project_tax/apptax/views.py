from django.shortcuts import render,redirect
from .forms import RegistrationForm,ContactForm,LoginForm,UserProfileForm,DocumentForm
from django.contrib.auth import authenticate, login, logout
from .models import OTP,CustomUser,Document,IncomeDetails,TaxCalculation,Deductions,BasicTaxDetail,Contact
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .cloudinary_config import * 
# Create your views here.
def home_view(request):
    return render(request,'general/home.html',)

import random

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Store the registration data in the session
            request.session['registration_data'] = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],  # Remember to hash it later
                'phone_number': form.cleaned_data.get('phone_number', None),  # Handle as necessary
                'pan_number': form.cleaned_data.get('pan_number'),  # Handle as necessary
                'annual_income': form.cleaned_data.get('annual_income', None),  # Handle as necessary
                'occupation': form.cleaned_data.get('occupation', None)  # Handle as necessary
            }
             # Generate a random OTP
            otp_value = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
            # Save the OTP in the database
            OTP.objects.create(email=form.cleaned_data['email'], otp=otp_value)
            # Send the OTP email
            send_otp_email(form.cleaned_data['email'], otp_value)
            return redirect('verify_otp')
        else:
            print(form.errors)  # Debugging output for errors
            
    else:
        form = RegistrationForm()
        
    return render(request, 'general/register.html', {'form': form})

def verify_otp(request):
    email = request.session.get('registration_data', {}).get('email', '')  # Get the email from session

    if request.method == 'POST':
        otp_value = request.POST.get('otp')
        email = request.POST.get('email')  # Retrieve email from the POST data
        
        # Verify OTP
        otp_entry = OTP.objects.filter(email=email, otp=otp_value).first()
        if otp_entry and otp_entry.is_valid():
            # Retrieve user data from session
            registration_data = request.session.get('registration_data')
            if registration_data:
                # Create the user
                user = CustomUser(
                    first_name=registration_data['first_name'],
                    last_name=registration_data['last_name'],
                    email=registration_data['email'],
                    phone_number=registration_data.get('phone_number'),  # Ensure this is included
                    pan_number=registration_data.get('pan_number'),  # Ensure this is included
                    annual_income=registration_data.get('annual_income'),  # Ensure this is included
                    occupation=registration_data.get('occupation'),  # Ensure this is included
                    taxpayer_status='Active'  # Set default value for taxpayer status
                )
                user.set_password(registration_data['password'])  # Hash the password
                user.save()  # Save the user to the database

                otp_entry.delete()  # Remove the used OTP
                del request.session['registration_data']  # Clear the session data
                return redirect('login')  # Redirect after successful registration
        else:
            # Handle invalid OTP case (e.g., show an error message)
            return render(request, 'general/verify_otp.html', {'error': 'Invalid OTP. Please try again.', 'email': email})

    # Render the OTP verification page with the email if GET request or session has expired
    return render(request, 'general/verify_otp.html', {'email': email})  # Pass email for the form

from django.core.mail import send_mail

def send_otp_email(email, otp_value):
    subject = 'Your OTP Code for Registration'
    message = (
        f'Hello,\n\n'
        f'Thank you for registering with our Smart-Tax System. '
        f'Your One-Time Password (OTP) for verification is: **{otp_value}**.\n\n'
        f'Please enter this OTP in the application to complete your registration.\n\n'
        f'This OTP is valid for 5 minutes. If you did not request this OTP, please ignore this email.\n\n'
        f'Thank you!'
    )
    
    # Send email
    send_mail(
        subject,
        message,
        'smarttaxsystems@gmail.com', 
        [email],
        fail_silently=False,
    )
def resend_otp(request):
    if request.method == "POST":
        email = request.POST.get('email')  # Make sure to pass the email in the POST request
        otp_value = random.randint(100000, 999999)  # Generate a new OTP value
        send_otp_email(email, otp_value)
        messages.success(request, 'A new OTP has been sent to your email.')
        return redirect('verify_otp')
def about_view(request):
    return render(request,'general/about.html')

def send_contact_email(name, email):
    subject = 'Your Response Has Been Received'
    message = (
        f'Dear {name},\n\n'
        'Thank you for reaching out to us! Your response has been received successfully. '
        'We will reply to you shortly.\n\n'
        'Best regards,\n'
        'Smart Tax System Team'
    )
    
    # Send email
    send_mail(
        subject,
        message,
        'smarttaxsystems@gmail.com',  # From email
        [email],                       # To email
        fail_silently=False,
    )

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the form data
            contact = form.save()
            # Get the name and email from the form
            name = form.cleaned_data.get('name')  # Adjust field names as per your form
            email = form.cleaned_data.get('email')  # Adjust field names as per your form

            # Send confirmation email
            send_contact_email(name, email)

            messages.success(request, "Your response was submitted successfully!")
            return redirect('contact')  # Redirect to the same page after submission
    else:
        form = ContactForm()
    
    return render(request, 'general/contact.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect to the appropriate dashboard based on user role
                if user.is_admin:
                    return redirect('admin_dashboard')  # Admin dashboard
                else:
                    return redirect('user_dashboard')  # User dashboard
            else:
                messages.error(request, "Invalid email or password.")  # Add error message
    else:
        form = LoginForm()

    return render(request, 'general/login.html', {'form': form})


import cloudinary.uploader

from django.db.models import Avg, Count, Sum
from decimal import Decimal
import json
def admin_dashboard(request):
    total_users=CustomUser.objects.count()

    total_documents = Document.objects.count()
    
    # Verified documents
    verified_documents = Document.objects.filter(verified=True).count()
    
    # Pending documents (i.e., not verified)
    pending_documents = total_documents - verified_documents

    total_calculations=TaxCalculation.objects.count()
    
    income_sources = IncomeDetails.objects.aggregate(
    basic_salary=Sum('basic_salary'),
    special_allowance=Sum('special_allowance'),
    hra=Sum('hra'),
    rental_income=Sum('rental_income'),
    interest_income=Sum('income_from_interest')
    )
    # Chart 1: Total Income Distribution by Age Group
    age_groups = {
        '18_30': 0, 
        '31_45': 0, 
        '46_60': 0, 
        '60_plus': 0
    }
    
    # Loop through each user in BasicTaxDetail to categorize them by age and income
    for user in BasicTaxDetail.objects.all():
        income = IncomeDetails.objects.filter(user=user.user_id).first().calculate_gross_income() if IncomeDetails.objects.filter(user=user.user_id).exists() else 0
        
        # Aggregate income by age group
        if 18 <= user.age <= 30:
            age_groups['18_30'] += income
        elif 31 <= user.age <= 45:
            age_groups['31_45'] += income
        elif 46 <= user.age <= 60:
            age_groups['46_60'] += income
        else:
            age_groups['60_plus'] += income

    # Chart 2: Tax Regime Comparison for Total Deductions
    old_regime_deductions = TaxCalculation.objects.filter(taxable_income_old_regime__gt=0).aggregate(total=Sum('total_deductions'))['total']
    new_regime_deductions = TaxCalculation.objects.filter(taxable_income_new_regime__gt=0).aggregate(total=Sum('total_deductions'))['total']

    # Chart 3: Top Exemptions Claimed by Users
    deductions = Deductions.objects.aggregate(
        section_80C=Sum('section_80C'),
        section_80D=Sum('section_80D'),
        section_80G=Sum('section_80G'),
        section_80E=Sum('section_80E'),
        section_80TTA=Sum('section_80TTA'),
    )
     
    # Chart 4: Feedback Ratings Distribution
    ratings = Feedback.objects.values('rating').annotate(count=Count('rating')).order_by('rating')
    ratings_data = list(ratings)  # Convert QuerySet to list of dictionaries

    # Pass data to the template
    context = {
        'age_groups': age_groups,
        'old_regime_deductions': old_regime_deductions,
        'new_regime_deductions': new_regime_deductions,
        'deductions': deductions,
        'ratings': json.dumps(ratings_data),  # Serialize ratings data for use in JavaScript
        'total_users':total_users,
        'total_documents':total_documents,
        'verified_documents':verified_documents,
        'pending_documents':pending_documents,
        'total_calculations':total_calculations,
        'income_sources': income_sources, 
    }
    return render(request, 'admin/admin_dashboard.html', context)

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
import base64
import numpy as np
from io import BytesIO
# Save plot to base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas



@login_required
def user_dashboard(request):
    # Fetching the income breakdown for the user
    try:
        income_details = IncomeDetails.objects.filter(user=request.user).first()
        income_breakdown = income_details is not None
        income_data = {
            'Basic': getattr(income_details, 'basic_salary', 0),
            'HRA': getattr(income_details, 'hra', 0),
            'Special': getattr(income_details, 'special_allowance', 0),
            'LTA': getattr(income_details, 'lta', 0),
            'Other': getattr(income_details, 'other_income', 0),
            'Rental': getattr(income_details, 'rental_income', 0),
            'Digital': getattr(income_details, 'income_from_digital_assets', 0)
        }
    except IncomeDetails.DoesNotExist:
        income_breakdown = False
        income_data = {}

    # Fetching deductions breakdown
    try:
        deductions = Deductions.objects.filter(user=request.user).first()
        deductions_breakdown = deductions is not None
        deductions_data = {
            'Section_80C': getattr(deductions, 'section_80C', 0),
            'Section_80D': getattr(deductions, 'section_80D', 0),
            'Section_80G': getattr(deductions, 'section_80G', 0),
            'Section_80E': getattr(deductions, 'section_80E', 0),
            'Section_80TTA': getattr(deductions, 'section_80TTA', 0)
        }
    except Deductions.DoesNotExist:
        deductions_breakdown = False
        deductions_data = {}

    # Fetching tax comparison for the user
    try:
        tax_details = TaxCalculation.objects.filter(user=request.user).order_by('entry_id').first()
        tax_comparison = tax_details is not None
        tax_comparison_data = {
            'Old_Regime': getattr(tax_details, 'tax_old_regime', 0),
            'New_Regime': getattr(tax_details, 'tax_new_regime', 0)
        }
    except TaxCalculation.DoesNotExist:
        tax_comparison = False
        tax_comparison_data = {}

    # Fetching document verification status
    document_status = {}
    documents = Document.objects.filter(user=request.user)
    for doc in documents:
        document_status[doc.document_type] = doc.verified

    # Fetching tax details for the current financial year
    financial_year = "FY 2024-2025"  # This should be dynamic based on the user's selection

    context = {
        'income_breakdown': income_breakdown,
        'income_data': income_data,
        'deductions_breakdown': deductions_breakdown,
        'deductions_data': deductions_data,
        'tax_comparison': tax_comparison,
        'tax_comparison_data': tax_comparison_data,
        'tax_details': tax_details,
        'financial_year': financial_year,
        'document_status': document_status
    }

    return render(request, 'user/user_dashboard.html', context)

@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)

        # Ensure email is appended if it's missing in POST data
        if not request.POST.get('email'):
            form.instance.email = user.email  # Use the current email if not provided

        if form.is_valid():
            profile_image = request.FILES.get('profile_image')
            if profile_image:
                # Upload to Cloudinary
                cloudinary_response = cloudinary.uploader.upload(profile_image)
                user.profile_image = cloudinary_response['secure_url']  # Save the URL

            form.save()  # Save other fields
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')  # Redirect to the profile page after update
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'user/user_profile.html', {'form': form, 'user': user})


def custom_logout(request):
    logout(request)  # Log out the user
    messages.success(request, "You have been logged out successfully.")  # Optional: Add a success message
    return redirect('home')  # Redirect to the home page

def document_management(request):
    # Retrieve the user's documents and their verification status
    user_documents = Document.objects.filter(user=request.user)
    
    # Dictionary to hold the verification status and latest document for each type
    doc_status = {
        'PAN': False,
        'TAX': False,
        'SALARY': False,
        'OTHER': False,
    }

    # Dictionary to hold the latest uploaded document for each type
    doc_files = {
        'PAN': None,
        'TAX': None,
        'SALARY': None,
        'OTHER': None,
    }

    # Update dictionaries based on the user's documents
    for doc in user_documents:
        if doc.document_type in doc_status:
            # Update verification status
            if doc.verified:
                doc_status[doc.document_type] = True
            
            # Set the latest document file for each type
            doc_files[doc.document_type] = doc  # Assuming `doc` has `document_file` and `uploaded_at` fields

    # Define document types metadata (name, description, and icon path)
    document_types = {
        'PAN': {'name': 'PAN Card', 'description': 'Upload your PAN card for verification.', 'icon': 'images/pan.png'},
        'TAX': {'name': 'Tax Paid Slip', 'description': 'Upload your tax paid slip for verification.', 'icon': 'images/tax.png'},
        'SALARY': {'name': 'Salary Slip', 'description': 'Upload your salary slip for verification.', 'icon': 'images/salary.png'},
        'OTHER': {'name': 'Other Document', 'description': 'Upload any other documents for verification.', 'icon': 'images/docs.jpg'},
    }

    context = {
        'doc_status': doc_status,
        'doc_files': doc_files,
        'document_types': document_types,
    }
    
    return render(request, 'user/document_management.html', context)

@login_required
def upload_document(request, doc_type):
    valid_doc_types = dict(Document.DOCUMENT_TYPES).keys()
    if doc_type not in valid_doc_types:
        messages.error(request, "Invalid document type.")
        return redirect('document_management')
    
    document = Document.objects.filter(user=request.user, document_type=doc_type).first()
    is_update = document is not None

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        
        if form.is_valid():
            if document:
                # Update existing document
                document.document_file = form.cleaned_data['document_file']
                document.save()
                messages.success(request, f'Your {doc_type} document has been updated successfully.')
            else:
                # Create a new document if it doesn't exist
                form.instance.user = request.user
                form.instance.document_type = doc_type
                form.save()
                messages.success(request, f'Your {doc_type} document has been uploaded successfully.')

            return redirect('document_management')
    else:
        form = DocumentForm(instance=document)

    return render(request, 'user/upload_document.html', {
        'form': form,
        'doc_type': doc_type,
        'is_update': is_update,
        'document': document  # Ensure document is passed to the template
    })


from django.http import FileResponse
from django.shortcuts import get_object_or_404
from decimal import InvalidOperation
def download_document(request, doc_id):
    # Get the document object or return 404 if not found
    document = get_object_or_404(Document, id=doc_id, user=request.user)

    # Create a file response to serve the file
    response = FileResponse(document.document_file.open(), as_attachment=True, filename=document.document_file.name)
    return response

from .forms import IncomeDetailsForm, DeductionsForm, TaxCalculationForm

@login_required
def tax_calculation_base(request):
    return render(request, 'user/tax_calculation_base.html')

from django.shortcuts import get_object_or_404, redirect, render
from .forms import BasicTaxDetailForm, IncomeDetailsForm, DeductionsForm
from django.http import Http404
from django.core.mail import send_mail
from decimal import Decimal

# Basic Details View
def basic_details_view(request):
    if request.method == "POST":
        form = BasicTaxDetailForm(request.POST)
        if form.is_valid():
            tax_detail = form.save(commit=False)
            tax_detail.user = request.user  # Link to the logged-in user
            tax_detail.save()

            print(f"Generated entry_id for Basic Tax Detail: {tax_detail.entry_id}")
            return redirect('income', uuid=tax_detail.entry_id)
    else:
        form = BasicTaxDetailForm()

    return render(request, 'user/basic_details.html', {'form': form})

# Income View
def income_view(request, uuid):
    # Try to get the related BasicTaxDetail entry by UUID, or create a new entry if it doesn't exist
    basic_tax_entry = get_object_or_404(BasicTaxDetail, entry_id=uuid, user=request.user)

    # Try to get the related Income entry by the BasicTaxDetail, or create a new entry
    try:
        income_entry = IncomeDetails.objects.get(entry_id=basic_tax_entry, user=request.user)
    except IncomeDetails.DoesNotExist:
        # If no entry exists, create a new IncomeDetails entry with the BasicTaxDetail instance
        income_entry = IncomeDetails.objects.create(entry_id=basic_tax_entry, user=request.user)

    # Handle the form submission to update the income entry
    if request.method == 'POST':
        form = IncomeDetailsForm(request.POST, instance=income_entry)
        if form.is_valid():
            form.save()  # Save the form data to the existing or newly created entry
            # Redirect to the next page (e.g., deductions view), passing the UUID of the BasicTaxDetail
            return redirect('deductions', uuid=basic_tax_entry.entry_id)
    else:
        form = IncomeDetailsForm(instance=income_entry)

    return render(request, 'user/income.html', {'form': form, 'income_entry': income_entry})

def deductions_view(request, uuid):
    # Corrected query using entry_id instead of uuid
    basic_detail = get_object_or_404(BasicTaxDetail, entry_id=uuid, user=request.user)

    deductions, created = Deductions.objects.get_or_create(
        entry_id=basic_detail, user=request.user
    )

    if request.method == 'POST':
        form = DeductionsForm(request.POST, instance=deductions)
        if form.is_valid():
            # Save form data to the deductions instance
            form.save()
            # Redirect to the tax calculation page after successful update
            return redirect('tax_calculation', uuid=basic_detail.entry_id)
    else:
        # Pre-fill form with existing data if GET request
        form = DeductionsForm(instance=deductions)

    return render(request, 'user/deductions.html', {'form': form, 'basic_detail': basic_detail})
# Tax Calculation View
from django.shortcuts import get_object_or_404
from .models import BasicTaxDetail, IncomeDetails, Deductions, TaxCalculation
import logging
logger = logging.getLogger(__name__)
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.urls import reverse

def tax_calculation_view(request, uuid):

    if not request.user.is_authenticated:
    # Handle the case when the user is not authenticated, e.g., redirect to login
        return redirect('login')
    try:
        basic_tax_entry = get_object_or_404(BasicTaxDetail, entry_id=uuid, user=request.user)

        try:
            income_details = IncomeDetails.objects.get(entry_id=basic_tax_entry, user=request.user)
        except IncomeDetails.DoesNotExist:
            income_details = IncomeDetails.objects.create(entry_id=basic_tax_entry, user=request.user)
            income_details.save()

        # Calculate Gross Income
        gross_income = sum([Decimal(getattr(income_details, field)) for field in [
            'basic_salary', 'hra', 'special_allowance', 'lta', 
            'other_allowance', 'rental_income', 'income_from_interest', 
            'income_from_digital_assets', 'other_income']])

        try:
            deductions = Deductions.objects.get(entry_id=basic_tax_entry, user=request.user)
        except Deductions.DoesNotExist:
            deductions = Deductions.objects.create(entry_id=basic_tax_entry, user=request.user)
            deductions.save()

        # Calculate total deductions
        total_deductions_old_regime = sum([Decimal(getattr(deductions, field)) for field in [
            'section_80C', 'section_80D', 'section_80G', 'section_80E', 
            'section_80TTA', 'standard_deduction_old']])

        total_deductions_new_regime = sum([Decimal(getattr(deductions, field)) for field in [
             'standard_deduction_new']])

        # Calculate taxable income for both regimes
        taxable_income_old_regime = gross_income - total_deductions_old_regime
        taxable_income_new_regime = gross_income - total_deductions_new_regime

        # Fetch the user's age
        age = basic_tax_entry.age

        # Tax Slab Calculation Function
        def calculate_tax(taxable_income, is_old_regime=True):
            if age < 60:
                if taxable_income <= Decimal('250000'):
                    return Decimal('0')
                elif taxable_income <= Decimal('500000'):
                    return taxable_income * Decimal('0.05')
                elif taxable_income <= Decimal('1000000'):
                    return taxable_income * Decimal('0.10')
                else:
                    return taxable_income * Decimal('0.20')
            elif age >= 60 and age < 80:  # Senior Citizens
                if taxable_income <= Decimal('300000'):
                    return Decimal('0')
                elif taxable_income <= Decimal('500000'):
                    return taxable_income * Decimal('0.05')
                elif taxable_income <= Decimal('1000000'):
                    return taxable_income * Decimal('0.20')
                else:
                    return taxable_income * Decimal('0.20')
            else:  # Super Senior Citizens
                if taxable_income <= Decimal('500000'):
                    return Decimal('0')
                elif taxable_income <= Decimal('1000000'):
                    return taxable_income * Decimal('0.20')
                else:
                    return taxable_income * Decimal('0.30')

        # Tax Calculation for both regimes
        tax_old_regime = calculate_tax(taxable_income_old_regime, True)
        tax_new_regime = calculate_tax(taxable_income_new_regime, False)

        # Health and Education Cess
        cess_old_regime = tax_old_regime * Decimal('0.04')
        cess_new_regime = tax_new_regime * Decimal('0.04')

        total_tax_old_regime = tax_old_regime + cess_old_regime
        total_tax_new_regime = tax_new_regime + cess_new_regime
        
        print("User:", request.user)  # Check if the user object is correct
        tax_calculation, created = TaxCalculation.objects.get_or_create(
        entry_id=basic_tax_entry, user=request.user)
        # Save the tax calculation in the model if necessary
        tax_calculation, created = TaxCalculation.objects.get_or_create(entry_id=basic_tax_entry)
        tax_calculation.user = request.user
        tax_calculation.gross_income = gross_income
        tax_calculation.total_deductions = total_deductions_old_regime  # Or the appropriate total deductions
        tax_calculation.taxable_income_old_regime = taxable_income_old_regime
        tax_calculation.taxable_income_new_regime = taxable_income_new_regime
        tax_calculation.tax_old_regime = total_tax_old_regime
        tax_calculation.tax_new_regime = total_tax_new_regime
        tax_calculation.save()

        # Fetch the financial year
        financial_year = basic_tax_entry.financial_year

        if request.method == 'POST':
            # Generate the email content
            html_content = render_to_string('user/send_tax_report.html', {
                'tax_details': tax_calculation,
                'gross_income': gross_income,
                'total_deductions_old_regime': total_deductions_old_regime,
                'total_deductions_new_regime': total_deductions_new_regime,
                'taxable_income_old_regime': taxable_income_old_regime,
                'taxable_income_new_regime': taxable_income_new_regime,
                'tax_old_regime': total_tax_old_regime,
                'tax_new_regime': total_tax_new_regime,
            })

            # Send the email
            send_mail(
                'Your Tax Calculation Report',
                'Please find attached your tax calculation details.',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                html_message=html_content,  # HTML content
            )

            # Redirect to a confirmation page after email is sent
            return render(request,'user/send_tax_report.html',
                          {
                'tax_details': tax_calculation,
                'gross_income': gross_income,
                'total_deductions_old_regime': total_deductions_old_regime,
                'total_deductions_new_regime': total_deductions_new_regime,
                'taxable_income_old_regime': taxable_income_old_regime,
                'taxable_income_new_regime': taxable_income_new_regime,
                'tax_old_regime': total_tax_old_regime,
                'tax_new_regime': total_tax_new_regime,
            })

        return render(request, 'user/tax_calculation.html', {
            'gross_income': gross_income,
            'total_deductions_old_regime': total_deductions_old_regime,
            'total_deductions_new_regime': total_deductions_new_regime,
            'taxable_income_old_regime': taxable_income_old_regime,
            'taxable_income_new_regime': taxable_income_new_regime,
            'tax_old_regime': total_tax_old_regime,
            'tax_new_regime': total_tax_new_regime,
            'financial_year': financial_year,
        })

    except IncomeDetails.DoesNotExist:
        return render(request, 'error.html', {'error_message': 'No IncomeDetails found for the given user and entry.'})

    except Deductions.DoesNotExist:
        return render(request, 'error.html', {'error_message': 'No Deductions found for the given user and entry.'})

from .forms import FeedbackForm
from .models import Feedback
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        user=request.user
        if form.is_valid():
            # Save feedback data
            feedback = form.save(commit=False)
            feedback.user = request.user  # Associate feedback with the logged-in user
            feedback.save()

            # Send success message
            messages.success(request, 'Your feedback has been submitted successfully!')
            
            # Send an email notification with the feedback details
            return redirect('feedback')  # Redirect to the feedback page or wherever you want
    else:
        form = FeedbackForm()

    # This is the range for displaying 5 stars in the template
    star_range = range(1, 6)
    return render(request, 'user/feedback.html', {'form': form, 'star_range': star_range})

def manage_users(request):
    # Get all users (CustomUser in your case)
    users = CustomUser.objects.all()
    return render(request, 'admin/manage_users.html', {'users': users})

def view_user(request, user_id):
    # Fetch the user by ID or return a 404 if not found
    user = get_object_or_404(CustomUser, id=user_id)

    return render(request, 'admin/view_user.html', {'user': user})

def edit_user(request, user_id):
    # Fetch the user to edit
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        # If the form is submitted, process the data
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')  # Redirect back to Manage Users page after saving
    else:
        # Create the form with the current user data
        form = UserProfileForm(instance=user)

    return render(request, 'admin/edit_user.html', {'form': form, 'user': user})

def delete_user(request, user_id):
    # Fetch the user to delete
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user.delete()  # Delete the user
        return redirect('manage_users')  # Redirect to Manage Users page after deletion

    return render(request, 'admin/confirm_delete.html', {'user': user})

def manage_documents(request):
    # Get all documents, grouped by user
    documents = Document.objects.all()
    return render(request, 'admin/manage_documents.html', {'documents': documents})

def approve_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    # Set verified to True
    document.verified = True
    document.save()

    # Send approval email
    send_mail(
        'Document Approved',
        'Your document has been approved.',
        settings.EMAIL_HOST_USER, # Your new Gmail address
        [document.user.email],  # recipient email
        fail_silently=False,
    )

    messages.success(request, f'{document.document_type} document approved successfully.')
    return redirect('manage_documents')

def disapprove_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    # Send disapproval email
    send_mail(
        'Document Disapproved',
        'Your document has been disapproved.',
        settings.EMAIL_HOST_USER,  # sender email
        [document.user.email],  # recipient email
        fail_silently=False,
    )

    # Delete the document
    document.delete()
    
    messages.success(request, f'{document.document_type} document disapproved and deleted.')
    return redirect('manage_documents')

# View all feedbacks
def view_feedbacks(request):
    feedbacks = Feedback.objects.all()  # Get all feedbacks
    contacts = Contact.objects.all()
    return render(request, 'admin/view_feedbacks.html', {
        'feedbacks': feedbacks,
        'contacts': contacts
        })

# Reply to feedback (email)
def reply_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Set up the email details
    feedback_details = (
        f"Dear {feedback.user.first_name},\n\n"
        "Thank you for your feedback! We truly appreciate your time and effort in helping us improve our services.\n\n"
        "Here are the details of the feedback we received:\n\n"
        f"- Calculation Type: {feedback.calculation_type}\n"
        f"- Feedback: {feedback.feedback_text}\n"
        f"- Rating: {feedback.rating} stars\n\n"
        "We value your input and will take it into consideration to enhance your experience.\n\n"
        "Best regards,\nSmartAx Systems"
    )

    try:
        send_mail(
            'Feedback Received',
            feedback_details,
            settings.DEFAULT_FROM_EMAIL,  # Make sure this is set in settings.py
            [feedback.user.email],  # Send to the feedback user's email
            fail_silently=False,
        )
        messages.success(request, "Reply sent successfully.")
    except Exception as e:
        messages.error(request, f"Failed to send reply: {e}")
    
    return redirect('manage_feedbacks')

from .forms import AdminNoteForm

def user_tax_calculations(request):
    tax_calculations = TaxCalculation.objects.select_related('user').all()

    if request.method == 'POST':
        # Retrieve selected tax calculation entry ID and note content
        selected_entry_id = request.POST.get('selected_entry')
        note_content = request.POST.get('note_content')

        # Get the selected tax calculation entry
        tax_entry = get_object_or_404(TaxCalculation, id=selected_entry_id)
        user = tax_entry.user

        # Send an email with the note about the selected calculation
        email_subject = f"Personal Note Regarding Your Tax Calculation (ID: {tax_entry.id})"
        email_body = (
            f"Dear {user.first_name},\n\n"
            f"This is a personal note from our team regarding your recent tax calculation:\n\n"
            f"{note_content}\n\n"
            f"Best regards,\nSmartAx Systems"
        )
        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return redirect('tax_calculations')

    return render(request, 'admin/tax_calculations.html', {
        'tax_calculations': tax_calculations,
    })