from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from account.managers import CustomUserManager
# from jobapp.models import Category # REMOVED: Causes circular import


class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYER = 'employer', _('Employer')
        EMPLOYEE = 'employee', _('Employee')

    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')

    username = None
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True, null=True) # Made gender optional
    company_name = models.CharField(max_length=100, blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    # Changed to string reference to avoid circular import
    hiring_categories = models.ManyToManyField('jobapp.Category', blank=True, help_text=_('Categories of workers you typically hire'))
    
    # Employee profile fields
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text=_('Contact phone number'))
    cv = models.FileField(upload_to='cvs/', blank=True, null=True, help_text=_('Upload your CV/Resume (PDF, DOC, DOCX)'))
    skills = models.TextField(blank=True, null=True, help_text=_('Comma-separated list of skills (e.g., Python, Django, JavaScript)'))
    years_of_experience = models.IntegerField(blank=True, null=True, help_text=_('Years of professional experience'))
    preferred_job_title = models.CharField(max_length=100, blank=True, null=True, help_text=_('e.g., Software Engineer, Data Analyst'))
    location = models.CharField(max_length=100, blank=True, null=True, help_text=_('City/Region where you are located'))
    bio = models.TextField(blank=True, null=True, help_text=_('Brief professional bio or about you'))


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class OutgoingEmail(models.Model):
    """Simple model to store outgoing emails for auditing and retrieval.
    The password-reset flow will send emails using a backend that saves here.
    """
    subject = models.CharField(max_length=255)
    body = models.TextField()
    to_emails = models.TextField(help_text='Comma-separated recipient emails')
    from_email = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Email to {self.to_emails} - {self.subject}"


class DomesticWorker(models.Model):
    """
    Model for domestic service workers.
    """
    SERVICE_CHOICES = [
        ('Housemaid', 'Housemaid'),
        ('Gatekeeper / Security', 'Gatekeeper / Security'),
        ('Saloonist / Hairdresser', 'Saloonist / Hairdresser'),
        ('Barber', 'Barber'),
        ('Gardener', 'Gardener'),
        ('Driver', 'Driver'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='domestic_profile')
    national_id = models.CharField(max_length=20, unique=True, verbose_name="Kenyan National ID")
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.service_type}"


class DomesticJob(models.Model):
    """
    Model for domestic job postings.
    """
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='domestic_jobs')
    title = models.CharField(max_length=255)
    service_category = models.CharField(max_length=50, choices=DomesticWorker.SERVICE_CHOICES)
    location = models.CharField(max_length=100)
    description = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} in {self.location}"
