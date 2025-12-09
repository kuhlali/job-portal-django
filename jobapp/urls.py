from django.urls import path
from django.views.generic import TemplateView # Import TemplateView
from jobapp import views

app_name = "jobapp"


urlpatterns = [

    # --- General Site Pages ---
    path('', views.home_view, name='home'),
    path('jobs/', views.JobListView.as_view(), name='job-list'),
    path('result/', views.search_result_view, name='search_result'),
    path('about/', TemplateView.as_view(template_name='jobapp/about.html'), name='about'),
    path('contact/', views.contact_view, name='contact'),

    # --- Dashboard URLs (Specific before Generic) ---
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/employer/job/<int:id>/applicants/', views.all_applicants_view, name='applicants'),
    path('dashboard/employer/job/edit/<int:id>/', views.JobUpdateView.as_view(), name='edit-job'),
    path('dashboard/employer/applicant/<int:id>/', views.applicant_details_view, name='applicant-details'),
    path('dashboard/employer/close/<int:id>/', views.make_complete_job_view, name='complete'),
    path('dashboard/employer/delete/<int:id>/', views.JobDeleteView.as_view(), name='delete'),
    path('dashboard/employee/delete-bookmark/<int:id>/', views.BookmarkDeleteView.as_view(), name='delete-bookmark'),
    
    # --- Domestic Job URLs (Specific before Generic) ---
    path('domestic-jobs/', views.domestic_job_list_view, name='domestic-job-list'), # Matches /domestic-jobs/
    path('domestic-jobs/post/', views.post_domestic_job_view, name='post-domestic-job'), # Matches /domestic-jobs/post/
    path('domestic-jobs/<int:id>/', views.domestic_job_detail_view, name='domestic-job-single'), # Matches /domestic-jobs/5/

    # --- Regular Job URLs (Specific before Generic) ---
    path('job/create/', views.JobCreateView.as_view(), name='create-job'),
    path('job/<int:id>/', views.JobDetailView.as_view(), name='single-job'),
    path('job/<int:id>/apply/', views.apply_job_view, name='apply-job'),
    path('job/<int:id>/bookmark/', views.job_bookmark_view, name='bookmark-job'),
]
