from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    EmployeeRegistrationView,
    HouseholdRegistrationView,
    CompanyRegistrationView,
    EmployeeProfileUpdateView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView, DomesticWorkerRegistrationView
)

app_name = "account"

urlpatterns = [
    path('employee/register/', EmployeeRegistrationView.as_view(), name='employee-registration'),
    path('household/register/', HouseholdRegistrationView.as_view(), name='household-registration'),
    path('company/register/', CompanyRegistrationView.as_view(), name='company-registration'),
    path('profile/edit/', EmployeeProfileUpdateView.as_view(), name='edit-profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # URLs for Domestic Worker and Jobs
    path('register/domestic-worker/', DomesticWorkerRegistrationView.as_view(), name='domestic-worker-registration')
]
