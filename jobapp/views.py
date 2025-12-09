from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from account.models import User, DomesticJob
from jobapp.forms import JobForm, JobEditForm, ContactForm
from account.forms import DomesticJobForm
from jobapp.models import Job, JobType, ExperienceLevel, WorkArrangement, Category, Applicant, BookmarkJob # Import all necessary models
from jobapp.permission import *

User = get_user_model()


def home_view(request):
    published_jobs = Job.objects.filter(is_published=True, is_closed=False).order_by('-created_at')
    total_candidates = User.objects.filter(role='employee').count()
    total_companies = User.objects.filter(role='employer').count()
    paginator = Paginator(published_jobs, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.is_ajax():
        job_list = list(page_obj.object_list.values('id', 'title', 'location', 'job_type', 'company_name', 'url'))
        
        data = {
            'job_lists': job_list,
            'current_page_no': page_obj.number,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'no_of_page': paginator.num_pages,
            'prev_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        }
        return JsonResponse(data)

    context = {
        'total_candidates': total_candidates,
        'total_companies': total_companies,
        'total_jobs': published_jobs.count(),
        'total_completed_jobs': Job.objects.filter(is_published=True, is_closed=True).count(),
        'page_obj': page_obj,
        'job_type_choices': JobType.choices, # Added for search form
        'experience_level_choices': ExperienceLevel.choices, # Added for search form
        'work_arrangement_choices': WorkArrangement.choices, # Added for search form
    }
    return render(request, 'jobapp/index.html', context)


class JobListView(ListView):
    model = Job
    template_name = 'jobapp/job-list.html'
    context_object_name = 'page_obj'
    paginate_by = 12
    # queryset = Job.objects.filter(is_published=True, is_closed=False).order_by('-created_at') # Will be set in get_queryset

    def get_queryset(self):
        queryset = Job.objects.filter(is_published=True, is_closed=False)
        sort_by = self.request.GET.get('sort_by', '-created_at') # Default to newest first

        if sort_by == 'oldest_first':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'salary_high_low':
            # Assuming salary is a numeric field or can be converted for sorting
            # For now, sorting as string, consider converting to IntegerField for proper numeric sort
            queryset = queryset.order_by('-salary') 
        elif sort_by == 'salary_low_high':
            queryset = queryset.order_by('salary')
        elif sort_by == 'title_asc':
            queryset = queryset.order_by('title')
        else: # Default or 'newest_first'
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job_type_choices'] = JobType.choices
        context['experience_level_choices'] = ExperienceLevel.choices
        context['work_arrangement_choices'] = WorkArrangement.choices
        context['current_sort_by'] = self.request.GET.get('sort_by', '-created_at') # Pass current sort to template
        return context


class JobDetailView(DetailView):
    model = Job
    template_name = 'jobapp/job-single.html'
    context_object_name = 'job'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_job_list = self.object.tags.similar_objects()
        paginator = Paginator(related_job_list, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['total'] = len(related_job_list)
        return context


class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobapp/post-job.html'
    success_url = reverse_lazy('jobapp:dashboard')

    def test_func(self):
        print(f"DEBUG: User role in JobCreateView test_func: {self.request.user.role}") # Added debug print
        return self.request.user.role == 'employer'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'You have successfully posted your job! Please wait for review.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    form_class = JobEditForm
    template_name = 'jobapp/job-edit.html'
    pk_url_kwarg = 'id'

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self):
        messages.success(self.request, 'Your Job Post Was Successfully Updated!')
        return reverse('jobapp:single-job', kwargs={'id': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


def search_result_view(request):
    job_list = Job.objects.filter(is_published=True, is_closed=False).order_by('-created_at')

    job_title = request.GET.get('job_title_or_company_name')
    location = request.GET.get('location')
    job_type = request.GET.get('job_type')
    experience_level = request.GET.get('experience_level')
    work_arrangement = request.GET.get('work_arrangement')

    if job_title:
        job_list = job_list.filter(Q(title__icontains=job_title) | Q(company_name__icontains=job_title))
    if location:
        job_list = job_list.filter(location__icontains=location)
    if job_type:
        job_list = job_list.filter(job_type__iexact=job_type)
    if experience_level:
        job_list = job_list.filter(experience_level=experience_level)
    if work_arrangement:
        job_list = job_list.filter(work_arrangement=work_arrangement)

    paginator = Paginator(job_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'job_type_choices': JobType.choices,
        'experience_level_choices': ExperienceLevel.choices,
        'work_arrangement_choices': WorkArrangement.choices,
    }
    return render(request, 'jobapp/result.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def apply_job_view(request, id):
    try:
        job = get_object_or_404(Job, id=id)
    except Http404:
        messages.error(request, 'Job posting not found.')
        return redirect('jobapp:job-list')
    
    if Applicant.objects.filter(user=request.user, job=job).exists():
        messages.error(request, 'You have already applied for this job!')
        return redirect('jobapp:single-job', id=id)

    Applicant.objects.create(user=request.user, job=job)
    messages.success(request, 'You have successfully applied for this job!')
    return redirect('jobapp:single-job', id=id)


@login_required(login_url=reverse_lazy('account:login'))
def dashboard_view(request):
    context = {}
    if request.user.role == 'employer':
        context['jobs'] = Job.objects.filter(user=request.user).annotate(applicant_count=Count('applicant'))
    elif request.user.role == 'employee':
        context['savedjobs'] = BookmarkJob.objects.filter(user=request.user)
        context['appliedjobs'] = Applicant.objects.filter(user=request.user)
    
    return render(request, 'jobapp/dashboard.html', context)


class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    template_name = 'jobapp/confirm_delete.html' # You need to create this template
    success_url = reverse_lazy('jobapp:dashboard')
    pk_url_kwarg = 'id'

    def test_func(self):
        return self.request.user == self.get_object().user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Your Job Post was successfully deleted!')
        return super().delete(request, *args, **kwargs)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def make_complete_job_view(request, id):
    job = get_object_or_404(Job, id=id, user=request.user)
    job.is_closed = True
    job.save()
    messages.success(request, 'Your Job was marked closed!')
    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def all_applicants_view(request, id):
    all_applicants = Applicant.objects.filter(job_id=id)
    context = {
        'all_applicants': all_applicants,
    }
    return render(request, 'jobapp/all-applicants.html', context)


class BookmarkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BookmarkJob
    success_url = reverse_lazy('jobapp:dashboard')
    pk_url_kwarg = 'id'

    def test_func(self):
        return self.request.user == self.get_object().user

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs) # Bookmarks can be deleted with a GET request

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Saved Job was successfully deleted!')
        return super().delete(request, *args, **kwargs)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def applicant_details_view(request, id):
    applicant = get_object_or_404(User, id=id)
    context = {
        'applicant': applicant,
    }
    return render(request, 'jobapp/applicant-details.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def job_bookmark_view(request, id):
    job = get_object_or_404(Job, id=id)
    if BookmarkJob.objects.filter(user=request.user, job=job).exists():
        messages.error(request, 'You have already saved this job!')
    else:
        BookmarkJob.objects.create(user=request.user, job=job)
        messages.success(request, 'You have successfully saved this job!')
    return redirect('jobapp:single-job', id=id)


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # In a real application, you would add logic here to send an email.
            messages.success(request, 'Your message has been sent successfully! We will get back to you shortly.')
            return redirect('jobapp:contact')
    else:
        form = ContactForm()

    context = {
        'form': form
    }
    return render(request, 'jobapp/contact.html', context)


@login_required
def post_domestic_job_view(request):
    # Ensure only users with the 'Employer' role can post jobs
    if request.user.role != User.Role.EMPLOYER:
        messages.error(request, "You do not have permission to post a job. Please register as an employer.")
        return redirect('jobapp:home')

    if request.method == 'POST':
        form = DomesticJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, 'Your job has been posted successfully!')
            return redirect('jobapp:home') # Or a 'my jobs' page
    else:
        form = DomesticJobForm()
    return render(request, 'jobapp/post_domestic_job.html', {'form': form})


@login_required
def domestic_job_list_view(request):
    """
    Displays a list of all active domestic jobs.
    """
    job_list = DomesticJob.objects.filter(is_active=True).order_by('-posted_on')
    
    paginator = Paginator(job_list, 10) # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobapp/domestic_job_list.html', {'page_obj': page_obj})


@login_required
def domestic_job_detail_view(request, id):
    """
    Displays the details of a single domestic job.
    """
    job = get_object_or_404(DomesticJob, id=id, is_active=True)
    context = {'job': job}
    return render(request, 'jobapp/domestic_job_single.html', context)
