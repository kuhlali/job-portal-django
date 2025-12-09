from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.shortcuts import get_object_or_404, render, redirect

from .models import User, DomesticJob
from .forms import EmployeeRegistrationForm, HouseholdRegistrationForm, CompanyRegistrationForm, EmployeeProfileEditForm, DomesticWorkerRegistrationForm, DomesticJobForm
from jobapp.permission import user_is_employee


class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('jobapp:home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('account:login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You are successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/password_reset.html'
    email_template_name = 'account/password_reset_email.html'
    subject_template_name = 'account/password_reset_subject.txt'
    success_url = reverse_lazy('account:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class EmployeeRegistrationView(CreateView):
    model = User
    form_class = EmployeeRegistrationForm
    template_name = 'account/employee-registration.html'
    success_url = reverse_lazy('account:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Your account has been successfully created! Welcome.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('jobapp:home')


class HouseholdRegistrationView(CreateView):
    model = User
    form_class = HouseholdRegistrationForm
    template_name = 'account/household-registration.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Your account has been successfully created! Welcome.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('jobapp:home')


class CompanyRegistrationView(CreateView):
    model = User
    form_class = CompanyRegistrationForm
    template_name = 'account/company-registration.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Your company account has been successfully created! Welcome.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('jobapp:home')


class EmployeeProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EmployeeProfileEditForm
    template_name = 'account/employee-edit-profile.html'
    success_url = reverse_lazy('account:edit-profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'Your Profile Was Successfully Updated!')
        # Redirect to the same edit page
        return reverse_lazy('account:edit-profile')


class DomesticWorkerRegistrationView(CreateView):
    model = User
    form_class = DomesticWorkerRegistrationForm
    template_name = 'account/worker_registration.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Registration successful! Welcome.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('jobapp:home')
