
from django.shortcuts import render, redirect, get_object_or_404
from .forms import JobForm, ApplicationForm, SignUpForm
from .models import Job, Application
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
def home(request):
    query = request.GET.get('q')
    if query:
        jobs = Job.objects.filter(title__icontains=query) | Job.objects.filter(company_name__icontains=query) | Job.objects.filter(location__icontains=query)
    else:
        jobs = Job.objects.all()
    return render(request, 'jobportal/home.html', {'jobs': jobs})

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save user with commit=False to modify before saving
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.save()

            # Save profile info (created via signal)
            user.profile.is_employer = form.cleaned_data['is_employer']
            user.profile.save()

            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'jobportal/register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.profile.is_employer:
        return render(request, 'jobportal/employer_dashboard.html')
    else:
        return render(request, 'jobportal/applicant_dashboard.html')

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('my_jobs')
    else:
        form = JobForm()
    return render(request, 'jobportal/post_job.html', {'form': form})

@login_required
def my_jobs(request):
    jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'jobportal/my_jobs.html', {'jobs': jobs})

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'jobportal/job_detail.html', {'job': job})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            return redirect('dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'jobportal/apply_job.html', {'form': form, 'job': job})

@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = Application.objects.filter(job=job)

    # Handle status updates
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        action = request.POST.get('action')
        application = get_object_or_404(Application, id=app_id, job=job)
        if action == 'approve':
            application.status = 'Approved'
        elif action == 'reject':
            application.status = 'Rejected'
        application.save()
        return redirect('view_applicants', job_id=job.id)

    return render(request, 'jobportal/view_applicants.html', {'applications': applications, 'job': job})

@login_required
def my_applications(request):
    status_filter = request.GET.get('status')
    applications = Application.objects.filter(applicant=request.user)
    if status_filter:
        applications = applications.filter(status=status_filter)
    return render(request, 'jobportal/my_applications.html', {
        'applications': applications,
        'selected_status': status_filter
    })
