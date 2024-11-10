from django import forms
from .models import CustomUser,Contact,Document,IncomeDetails, Deductions, TaxCalculation,BasicTaxDetail


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'pan_number', 
                  'address', 'city', 'state', 'postal_code', 'occupation', 
                  'annual_income', 'taxpayer_status', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        # Validate that passwords match
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        return cleaned_data
    


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'location', 'email', 'message']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'date_of_birth', 'phone_number', 
            'pan_number', 'address', 'city', 'state', 'postal_code', 
            'occupation', 'annual_income', 'taxpayer_status', 'profile_image'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # Iterate over fields and update attributes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

            # Make specific fields unchangeable
            if field_name in ['email', 'taxpayer_status']:
                field.widget.attrs['disabled'] = 'disabled'  # Disable the field
                field.required = False  # Mark as not required

            # Mark other specific fields as optional
            if field_name in ['address', 'city', 'state', 'postal_code', 'occupation', 'annual_income']:
                field.required = False  # Mark these fields as not required

    def clean(self):
        cleaned_data = super().clean()

        # Optionally, you can remove any unwanted errors for unchangeable fields
        for field_name in ['email', 'taxpayer_status']:
            if field_name in cleaned_data:
                del cleaned_data[field_name]  # Remove them from cleaned data to prevent errors

        return cleaned_data
    
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_file']  # Add other fields if necessary
        widgets = {
            'document_file': forms.ClearableFileInput(attrs={'id': 'file-input', 'style': 'display: none;'})
        }

class BasicTaxDetailForm(forms.ModelForm):
    FINANCIAL_YEAR_CHOICES = [
        ('2024-2025', 'FY - 2024-2025 (Returns to be filed between 1st April 2025 - 31st March 2026)'),
        ('2023-2024', 'FY - 2023-2024 (Returns to be filed between 1st April 2024 - 31st March 2025)'),
        ('2022-2023', 'FY - 2022-2023 (Returns to be filed between 1st April 2023 - 31st March 2024)'),
        ('2021-2022', 'FY - 2021-2022 (Returns to be filed between 1st April 2022 - 31st March 2023)'),
        ('2020-2021', 'FY - 2020-2021 (Returns to be filed between 1st April 2021 - 31st March 2022)'),
    ]
    
    financial_year = forms.ChoiceField(choices=FINANCIAL_YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = BasicTaxDetail
        fields = ['financial_year', 'age']

class IncomeDetailsForm(forms.ModelForm):
    class Meta:
        model = IncomeDetails
        fields = ['basic_salary', 'hra', 'special_allowance', 'lta', 'other_allowance',
                  'hra_exempted', 'lta_exempted', 'income_from_interest', 'rental_income',
                  'interest_on_home_loan_self_occupied', 'interest_on_home_loan_let_out',
                  'income_from_digital_assets', 'other_income']



class DeductionsForm(forms.ModelForm):
    
    class Meta:
        model = Deductions
        fields = ['section_80C', 'section_80D', 'section_80G', 'section_80E', 'section_80TTA']

class TaxCalculationForm(forms.Form):
    regime = forms.ChoiceField(choices=[('old', 'Old Regime'), ('new', 'New Regime')], required=True)

from .models import Feedback

from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['calculation_type', 'feedback_text', 'rating']
    
    rating = forms.IntegerField(widget=forms.HiddenInput())

class ApproveDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['verified']
        widgets = {
            'verified': forms.CheckboxInput(attrs={'checked': 'checked'})
        }

class AdminNoteForm(forms.Form):
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a personal note here...'}),
        label='Personal Note',
    )