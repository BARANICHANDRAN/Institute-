from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard Home - redirects based on user type
    path('', views.dashboard_home, name='home'),
    
    # Admin Dashboard URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/students/', views.list_students, name='list_students'),
    path('admin/students/add/', views.add_student, name='add_student'),
    path('admin/students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('admin/students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('admin/students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('admin/students/<int:student_id>/toggle-status/', views.toggle_student_status, name='toggle_student_status'),
    path('admin/tasks/add/', views.add_task, name='add_task'),
    path('admin/submissions/', views.view_submissions, name='view_submissions'),
    path('admin/submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    
    # Student Dashboard URLs
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('student/tasks/<int:task_id>/start/', views.start_task, name='start_task'),
    path('student/tasks/<int:task_id>/submit/', views.submit_task, name='submit_task'),
    
    # API URLs for Code Execution
    path('api/code/execute/', views.execute_code, name='execute_code'),
] 