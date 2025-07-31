from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='jobportal/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/new/', views.post_job, name='post_job'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('my_jobs/', views.my_jobs, name='my_jobs'),
    path('applications/<int:job_id>/', views.view_applicants, name='view_applicants'),
    path('my-applications/', views.my_applications, name='my_applications'),
]
