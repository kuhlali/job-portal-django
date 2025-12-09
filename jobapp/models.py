from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager

User = get_user_model()


class JobType(models.TextChoices):
    FULL_TIME = 'FT', _('Full time')
    PART_TIME = 'PT', _('Part time')
    INTERNSHIP = 'IN', _('Internship')

class ExperienceLevel(models.TextChoices):
    ENTRY = 'EN', _('Entry Level')
    JUNIOR = 'JR', _('Junior')
    MID = 'MD', _('Mid-Level')
    SENIOR = 'SR', _('Senior')
    DIRECTOR = 'DR', _('Director')
    EXECUTIVE = 'EX', _('Executive')

class WorkArrangement(models.TextChoices):
    ONSITE = 'ON', _('On-site')
    REMOTE = 'RM', _('Remote')
    HYBRID = 'HB', _('Hybrid')


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Job(models.Model):
    user = models.ForeignKey(User, related_name='jobs', on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = RichTextField()
    tags = TaggableManager()
    location = models.CharField(max_length=300)
    job_type = models.CharField(choices=JobType.choices, max_length=2) # Changed max_length to 2
    experience_level = models.CharField(choices=ExperienceLevel.choices, max_length=2, blank=True, null=True)
    work_arrangement = models.CharField(choices=WorkArrangement.choices, max_length=2, blank=True, null=True)
    benefits = RichTextField(blank=True, null=True)
    category = models.ForeignKey(Category, related_name='jobs', on_delete=models.CASCADE)
    salary = models.CharField(max_length=30, blank=True)
    company_name = models.CharField(max_length=300)
    company_description = RichTextField(blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True) # Made URL optional
    last_date = models.DateField(blank=True, null=True) # Made last_date optional
    is_published = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job.title


class BookmarkJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job.title
