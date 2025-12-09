from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from jobapp.models import Job, Applicant, BookmarkJob, Category, JobType, ExperienceLevel, WorkArrangement
from ckeditor.widgets import CKEditorWidget

User = get_user_model()

class JobForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Job Title:"
        self.fields['location'].label = "Job Location:"
        self.fields['salary'].label = "Salary (Optional):"
        self.fields['description'].label = "Job Description:"
        self.fields['tags'].label = "Tags (Comma Separated):"
        self.fields['last_date'].label = "Submission Deadline (Optional):"
        self.fields['company_name'].label = "Company Name:"
        self.fields['url'].label = "Company Website (Optional):"
        self.fields['experience_level'].label = "Experience Level:"
        self.fields['work_arrangement'].label = "Work Arrangement:"
        self.fields['benefits'].label = "Benefits (Optional):"

        self.fields['title'].widget.attrs.update(
            {'placeholder': 'e.g., Software Developer'}
        )        
        self.fields['location'].widget.attrs.update(
            {'placeholder': 'e.g., Nairobi, Kenya'}
        )
        self.fields['salary'].widget.attrs.update(
            {'placeholder': 'e.g., $800 - $1200'}
        )
        self.fields['tags'].widget.attrs.update(
            {'placeholder': 'e.g., Python, JavaScript, Django'}
        )                        
        self.fields['last_date'].widget.attrs.update(
            {'placeholder': 'YYYY-MM-DD', 'class': 'form-control appointment_date'}
        )        
        self.fields['company_name'].widget.attrs.update(
            {'placeholder': 'e.g., KaziNyumbani Inc.'}
        )           
        self.fields['url'].widget.attrs.update(
            {'placeholder': 'https://www.example.com'}
        )    
        self.fields['benefits'].widget.attrs.update(
            {'placeholder': 'e.g., Health insurance, Remote work, Paid time off'}
        )

    class Meta:
        model = Job
        fields = [
            "title",
            "location",
            "job_type",
            "experience_level",
            "work_arrangement",
            "category",
            "salary",
            "description",
            "benefits",
            "tags",
            "last_date",
            "company_name",
            "company_description",
            "url"
        ]
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
        }


class JobApplyForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['job']

class JobBookmarkForm(forms.ModelForm):
    class Meta:
        model = BookmarkJob
        fields = ['job']


class JobEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Job Title:"
        self.fields['location'].label = "Job Location:"
        self.fields['salary'].label = "Salary (Optional):"
        self.fields['description'].label = "Job Description:"
        self.fields['last_date'].label = "Submission Deadline (Optional):"
        self.fields['company_name'].label = "Company Name:"
        self.fields['url'].label = "Company Website (Optional):"
        self.fields['experience_level'].label = "Experience Level:"
        self.fields['work_arrangement'].label = "Work Arrangement:"
        self.fields['benefits'].label = "Benefits (Optional):"

        self.fields['title'].widget.attrs.update(
            {'placeholder': 'e.g., Software Developer'}
        )        
        self.fields['location'].widget.attrs.update(
            {'placeholder': 'e.g., Nairobi, Kenya'}
        )
        self.fields['salary'].widget.attrs.update(
            {'placeholder': 'e.g., $800 - $1200'}
        )
        self.fields['last_date'].widget.attrs.update(
            {'placeholder': 'YYYY-MM-DD', 'class': 'form-control appointment_date'}
        )        
        self.fields['company_name'].widget.attrs.update(
            {'placeholder': 'e.g., KaziNyumbani Inc.'}
        )           
        self.fields['url'].widget.attrs.update(
            {'placeholder': 'https://www.example.com'}
        )    
        self.fields['benefits'].widget.attrs.update(
            {'placeholder': 'e.g., Health insurance, Remote work, Paid time off'}
        )

    class Meta:
        model = Job
        fields = [
            "title",
            "location",
            "job_type",
            "experience_level",
            "work_arrangement",
            "category",
            "salary",
            "description",
            "benefits",
            "tags", # Tags should be included in edit form
            "last_date",
            "company_name",
            "company_description",
            "url"
        ]
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=200, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
