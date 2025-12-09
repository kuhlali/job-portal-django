from django import forms
from .models import User, DomesticWorker, DomesticJob


class BaseRegistrationForm(forms.ModelForm):
    """Base form for user registration, handles password confirmation."""
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') and cd.get('password2') and cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class EmployeeRegistrationForm(BaseRegistrationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'gender', 'phone_number', 'location', 'preferred_job_title', 'bio', 'cv', 'skills', 'years_of_experience')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comma-separated list of skills (e.g., Python, Django, JavaScript)'}),
            'years_of_experience': forms.NumberInput(attrs={'min': 0}),
        }
        labels = {
            'cv': 'Upload your CV/Resume',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.EMPLOYEE
        if commit:
            user.save()
        return user


class HouseholdRegistrationForm(BaseRegistrationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'gender', 'phone_number', 'location')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.EMPLOYER # Households are employers
        if commit:
            user.save()
        return user


class CompanyRegistrationForm(BaseRegistrationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'company_name', 'company_logo', 'company_website')
        widgets = {
            'company_logo': forms.FileInput(),
        }
        labels = {
            'company_logo': 'Upload Company Logo',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.EMPLOYER # Companies are employers
        if commit:
            user.save()
        return user


class EmployeeProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'location',
            'bio', 'cv', 'skills', 'years_of_experience', 'preferred_job_title'
        ]
        # You can add widgets here for better UI, e.g., for 'bio' or 'skills'


class DomesticWorkerRegistrationForm(BaseRegistrationForm):
    national_id = forms.CharField(max_length=20, required=True, label="Kenyan National ID")
    service_type = forms.ChoiceField(choices=DomesticWorker.SERVICE_CHOICES)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'gender', 'phone_number')
        labels = {
            'gender': 'Gender',
            'phone_number': 'Phone Number'
        }

    def save(self, commit=True):
        # First, save the User instance
        user = super().save(commit=False)
        user.role = User.Role.EMPLOYEE # Set the user role
        if commit:
            user.save()
            # Then, create the related DomesticWorker profile
            DomesticWorker.objects.create(
                user=user,
                national_id=self.cleaned_data.get('national_id'),
                service_type=self.cleaned_data.get('service_type')
            )
        return user


class DomesticJobForm(forms.ModelForm):
    class Meta:
        model = DomesticJob
        fields = ['title', 'service_category', 'location', 'description']