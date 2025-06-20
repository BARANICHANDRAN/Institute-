from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import subprocess
import tempfile
import os
from datetime import datetime, timedelta
from .models import Student, Task, TaskSubmission, UserProfile
from .forms import StudentForm, TaskForm
from django.db.models import Q, Avg

def is_admin(user):
    try:
        profile = user.userprofile
        return profile.user_type == 'admin'
    except:
        return False

def is_student(user):
    try:
        profile = user.userprofile
        return profile.user_type == 'student'
    except:
        return False

@login_required
def dashboard_home(request):
    try:
        profile = request.user.userprofile
        if profile.user_type == 'admin':
            return redirect('dashboard:admin_dashboard')
        elif profile.user_type == 'student':
            return redirect('dashboard:student_dashboard')
        else:
            # Default fallback
            return redirect('dashboard:admin_dashboard')
    except:
        # If userprofile doesn't exist, create one as admin
        try:
            UserProfile.objects.create(user=request.user, user_type='admin')
            return redirect('dashboard:admin_dashboard')
        except:
            return redirect('login')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    students = Student.objects.filter(is_active=True)
    tasks = Task.objects.filter(is_active=True).order_by('-created_at')
    recent_submissions = TaskSubmission.objects.all().order_by('-submitted_at')[:10]
    
    context = {
        'students': students,
        'tasks': tasks,
        'recent_submissions': recent_submissions,
        'total_students': students.count(),
        'total_tasks': tasks.count(),
        'total_submissions': TaskSubmission.objects.count(),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    try:
        student = request.user.student
        completed_task_ids = TaskSubmission.objects.filter(student=student, status='completed').values_list('task_id', flat=True)
        active_tasks = Task.objects.filter(is_active=True, due_date__gte=timezone.now()).exclude(id__in=completed_task_ids).order_by('due_date')
        completed_tasks = TaskSubmission.objects.filter(student=student, status='completed')
        pending_tasks = TaskSubmission.objects.filter(student=student, status='pending')
        
        context = {
            'student': student,
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
        }
        return render(request, 'dashboard/student_dashboard.html', context)
    except:
        messages.error(request, 'Student profile not found.')
        return redirect('login')

@login_required
@user_passes_test(is_admin)
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            username = f"student_{student.student_id}"
            if User.objects.filter(username=username).exists():
                form.add_error('student_id', 'A user with this student ID already exists.')
            else:
                name_part = (student.full_name[:3].upper())
                dob_part = student.date_of_birth.strftime('%d')
                phone_part = student.phone[7:]
                password = f"{name_part}{dob_part}{phone_part}"
                user = User.objects.create_user(
                    username=username,
                    email=student.email,
                    password=password,
                    first_name=student.full_name.split()[0] if student.full_name else '',
                    last_name=' '.join(student.full_name.split()[1:]) if len(student.full_name.split()) > 1 else ''
                )
                student.user = user
                student.save()
                UserProfile.objects.create(user=user, user_type='student')
                messages.success(request, f'Student {student.full_name} added successfully!')
                return redirect('dashboard:admin_dashboard')
    else:
        form = StudentForm()
    return render(request, 'dashboard/add_student.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" added successfully!')
            return redirect('dashboard:admin_dashboard')
    else:
        form = TaskForm()
    
    return render(request, 'dashboard/add_task.html', {'form': form})

@login_required
@user_passes_test(is_student)
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, is_active=True)
    student = request.user.student
    
    # Check if submission exists
    submission, created = TaskSubmission.objects.get_or_create(
        student=student,
        task=task,
        defaults={'status': 'pending'}
    )
    
    context = {
        'task': task,
        'submission': submission,
    }
    return render(request, 'dashboard/task_detail.html', context)

@login_required
@user_passes_test(is_student)
def start_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, is_active=True)
    student = request.user.student
    
    submission, created = TaskSubmission.objects.get_or_create(
        student=student,
        task=task,
        defaults={'status': 'pending', 'code': ''}
    )
    
    # Always clear the code if the task is being started (not completed)
    if submission.status != 'completed' and submission.code:
        submission.code = ''
        submission.save(update_fields=['code'])
    
    if submission.status == 'completed':
        messages.warning(request, 'You have already completed this task.')
        return redirect('dashboard:task_detail', task_id=task_id)
    
    # Start timer
    start_time = timezone.now()
    request.session['task_start_time'] = start_time.isoformat()
    request.session['current_task_id'] = task_id
    
    context = {
        'task': task,
        'submission': submission,
        'start_time': start_time,
    }
    return render(request, 'dashboard/task_workspace.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def execute_code(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        language = data.get('language', 'python')
        input_data = data.get('input', '')
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute code with input
            result = subprocess.run(
                ['python', temp_file],
                input=input_data.encode(),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout
            error = result.stderr
            
            return JsonResponse({
                'success': True,
                'output': output,
                'error': error,
                'return_code': result.returncode
            })
        finally:
            # Clean up temporary file
            os.unlink(temp_file)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@user_passes_test(is_student)
def submit_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, is_active=True)
        student = request.user.student
        
        submission = get_object_or_404(TaskSubmission, student=student, task=task)
        
        # Get form data
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        
        # Calculate time taken
        start_time_str = request.session.get('task_start_time')
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str)
            time_taken = int((timezone.now() - start_time).total_seconds())
        else:
            time_taken = 0
        
        # Update submission
        submission.code = code
        submission.language = language
        submission.status = 'completed'
        submission.submitted_at = timezone.now()
        submission.time_taken = time_taken
        submission.save()
        
        # Clear session
        if 'task_start_time' in request.session:
            del request.session['task_start_time']
        if 'current_task_id' in request.session:
            del request.session['current_task_id']
        
        messages.success(request, 'Task submitted successfully!')
        return redirect('dashboard:task_detail', task_id=task_id)
    
    return redirect('task_detail', task_id=task_id)

@login_required
@user_passes_test(is_admin)
def view_submissions(request):
    submissions = TaskSubmission.objects.all().order_by('-submitted_at')
    return render(request, 'dashboard/view_submissions.html', {'submissions': submissions})

@login_required
@user_passes_test(is_admin)
def grade_submission(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    
    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback', '')
        
        if score is not None:
            try:
                submission.score = float(score)
                submission.feedback = feedback
                submission.status = 'graded'
                submission.save()
                messages.success(request, f'Submission graded successfully with score {score}.')
                return redirect('dashboard:view_submissions')
            except ValueError:
                messages.error(request, 'Invalid score. Please enter a valid number.')
    
    context = {
        'submission': submission,
    }
    return render(request, 'dashboard/grade_submission.html', context)

@login_required
@user_passes_test(is_admin)
def list_students(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'full_name')
    
    # Base queryset
    students = Student.objects.all()
    
    # Apply search filter
    if search_query:
        students = students.filter(
            Q(full_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter == 'active':
        students = students.filter(is_active=True)
    elif status_filter == 'inactive':
        students = students.filter(is_active=False)
    
    # Apply sorting
    if sort_by == 'student_id':
        students = students.order_by('student_id')
    elif sort_by == 'email':
        students = students.order_by('email')
    elif sort_by == 'created_at':
        students = students.order_by('-created_at')
    else:
        students = students.order_by('full_name')
    
    context = {
        'students': students,
        'total_students': students.count(),
        'active_students': students.filter(is_active=True).count(),
        'inactive_students': students.filter(is_active=False).count(),
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    return render(request, 'dashboard/list_students.html', context)

@login_required
@user_passes_test(is_admin)
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Get student's submissions
    submissions = TaskSubmission.objects.filter(student=student).order_by('-submitted_at')
    
    # Calculate statistics
    total_submissions = submissions.count()
    completed_submissions = submissions.filter(status='completed').count()
    graded_submissions = submissions.filter(status='graded').count()
    average_score = submissions.filter(score__isnull=False).aggregate(Avg('score'))['score__avg'] or 0
    
    context = {
        'student': student,
        'submissions': submissions[:10],  # Show last 10 submissions
        'total_submissions': total_submissions,
        'completed_submissions': completed_submissions,
        'graded_submissions': graded_submissions,
        'average_score': round(average_score, 2),
    }
    return render(request, 'dashboard/student_detail.html', context)

@login_required
@user_passes_test(is_admin)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name} updated successfully!')
            return redirect('dashboard:student_detail', student_id=student.id)
    else:
        form = StudentForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'dashboard/edit_student.html', context)

@login_required
@user_passes_test(is_admin)
def toggle_student_status(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student.is_active = not student.is_active
        student.save()
        
        status = 'activated' if student.is_active else 'deactivated'
        messages.success(request, f'Student {student.full_name} has been {status}.')
        
        return redirect('dashboard:list_students')
    
    return redirect('dashboard:student_detail', student_id=student_id)

@login_required
@user_passes_test(is_admin)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student_name = student.full_name
        student_id_value = student.student_id
        
        # Delete associated user and user profile
        if student.user:
            try:
                user_profile = student.user.userprofile
                user_profile.delete()
            except:
                pass
            student.user.delete()
        
        # Delete the student
        student.delete()
        
        messages.success(request, f'Student {student_name} (ID: {student_id_value}) has been deleted successfully.')
        return redirect('dashboard:list_students')
    
    context = {
        'student': student,
    }
    return render(request, 'dashboard/delete_student.html', context)
