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


@login_required
def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')


import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
import base64
import numpy as np
from io import BytesIO
# Save plot to base64


def save_plot_to_base64(fig):
    """Helper function to save matplotlib plot to base64."""
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

  # Import the filter

def user_dashboard(request):
    user = request.user

    # 1. Income Breakdown (Bar Chart)
    income_details = IncomeDetails.objects.filter(user=user).order_by('-id').first()
    basic_details = BasicTaxDetail.objects.filter(user=user).order_by('-id').first()
    if income_details:
        income_data = {
            'Basic': income_details.basic_salary or 0,
            'HRA': income_details.hra or 0,
            'Special': income_details.special_allowance or 0,
            'LTA': income_details.lta or 0,
            'Other': income_details.other_allowance or 0,
            'Rental': income_details.rental_income or 0,
            'Digital': income_details.income_from_digital_assets or 0,
        }
        # Remove zero or NaN entries to prevent issues in pie chart rendering
        income_data = {k: np.nan_to_num(v, nan=0) for k, v in income_data.items() if v > 0}
    else:
        income_data = {}

    if income_data:
        fig1, ax1 = plt.subplots()
        ax1.bar(income_data.keys(), income_data.values(), color='gold')
        ax1.set_xlabel('Income Sources')
        ax1.set_ylabel('Amount')
        ax1.set_title('Income Breakdown')
        income_breakdown = save_plot_to_base64(fig1)
    else:
        income_breakdown = None

    # 2. Old vs New Regime Tax Comparison (Bar Chart)
    tax_calculation = TaxCalculation.objects.filter(user=user).order_by('-id').first()
    if tax_calculation:
        tax_data = {
            'Old Regime': tax_calculation.tax_old_regime or 0,
            'New Regime': tax_calculation.tax_new_regime or 0,
        }
        tax_data = {k: np.nan_to_num(v, nan=0) for k, v in tax_data.items()}

        fig2, ax2 = plt.subplots()
        ax2.bar(tax_data.keys(), tax_data.values(), color=['#1f77b4', '#ff7f0e'])
        ax2.set_ylabel("Tax Amount")
        tax_comparison = save_plot_to_base64(fig2)
    else:
        tax_comparison = None

    # 3. Deductions Breakdown (Pie Chart)
    deductions = Deductions.objects.filter(user=user).order_by('-id').first()
    if deductions:
        deductions_data = {
            'Section 80C': deductions.section_80C or 0,
            'Section 80D': deductions.section_80D or 0,
            'Section 80G': deductions.section_80G or 0,
            'Section 80E': deductions.section_80E or 0,
            'Section 80TTA': deductions.section_80TTA or 0,
        }
        deductions_data = {k: np.nan_to_num(v, nan=0) for k, v in deductions_data.items() if v > 0}

        fig3, ax3 = plt.subplots()
        ax3.pie(deductions_data.values(), labels=deductions_data.keys(), autopct='%1.1f%%', startangle=90)
        ax3.axis('equal')
        deductions_breakdown = save_plot_to_base64(fig3)
    else:
        deductions_breakdown = None

    # 4. Income Comparison vs Taxable Income (Bar Chart)
    income_comparison = None  # You can define logic for this chart if needed

    # 5. Effective Tax Rate Over Years (Line Chart or other)
    tax_rate_chart = None  # Define logic for this chart if needed

    # Fetch the latest tax details for the user
    tax_details = TaxCalculation.objects.filter(user=user).order_by('-id').first()

    # 6. Document Verification Status
    documents = Document.objects.filter(user=user)
    document_status = {}
    for doc in ['PAN', 'TAX', 'SALARY', 'OTHER']:
        doc_obj = documents.filter(document_type=doc).first()
        if doc_obj:
            document_status[doc] = 'Verified' if doc_obj.verified else 'Not Verified'
        else:
            document_status[doc] = 'Not Updated'

    # Render the dashboard template with all the data
    context = {
        'income_breakdown': income_breakdown,
        'tax_comparison': tax_comparison,
        'deductions_breakdown': deductions_breakdown,
        'income_comparison': income_comparison,
        'tax_rate_chart': tax_rate_chart,
        'tax_details': tax_details,
        'document_status': document_status,
    }
    if basic_details and basic_details.financial_year is not None:
     context['financial_year'] = basic_details.financial_year

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