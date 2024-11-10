from django.urls import path
from .views import (
    home_view,
    register_view,
    verify_otp,
    login_view,
    about_view,
    contact_view,
    resend_otp,
    admin_dashboard,
    user_dashboard,
    user_profile,
    custom_logout,
    document_management,
    upload_document,
    download_document,

    tax_calculation_view,
    basic_details_view,
    income_view,
    deductions_view,
    submit_feedback,


    manage_users,
    delete_user,
    edit_user,
    delete_user,
    view_user,
    manage_documents,
    approve_document,
    disapprove_document,
    reply_feedback,
    view_feedbacks,
    user_tax_calculations
)

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',home_view,name='home'),
    path('register/',register_view,name='register'),
    path('register/verify_otp/',verify_otp,name='verify_otp'),
    path('login/',login_view,name='login'),
    path('about/',about_view,name='about'),
    path('contact/', contact_view, name='contact'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('logout/', custom_logout, name='logout'),
    path('admin_dashboard/',admin_dashboard, name='admin_dashboard'),
    path('user_dashboard/', user_dashboard, name='user_dashboard'),
    path('user_profile/', user_profile, name='user_profile'),
    path('document_management/', document_management, name='document_management'),
    path('upload/<str:doc_type>/',upload_document, name='upload_document'),
    path('documents/download/<int:doc_id>/', download_document, name='download_document'),
    
    path('basic-details/',basic_details_view, name='basic_details'),
    path('income/<uuid:uuid>/',income_view, name='income'),
    path('deductions/<uuid:uuid>/',deductions_view, name='deductions'),
    path('calculate/<uuid:uuid>/',tax_calculation_view, name='tax_calculation'),
    path('feedback',submit_feedback, name='feedback'),

    path('manage_user',manage_users, name='manage_users'),
     path('edit_user/<int:user_id>/', edit_user, name='edit_user'),

    # View User
    path('view_user/<int:user_id>/', view_user, name='view_user'),

    # Delete User
    path('delete_user/<int:user_id>/',delete_user, name='delete_user'),

    path('manage_documents/',manage_documents, name='manage_documents'),
    path('approve/<int:document_id>/', approve_document, name='approve_document'),
    path('disapprove/<int:document_id>/',disapprove_document, name='disapprove_document'),

    path('manage_feedbacks/',view_feedbacks, name='manage_feedbacks'),
    path('reply_feedback/<int:feedback_id>/',reply_feedback, name='reply_feedback'),

    path('tax_calculations/',user_tax_calculations, name='tax_calculations'),
]
