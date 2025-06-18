from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Student, Task, TaskSubmission, UserProfile

class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'email', 'enrollment_date', 'is_active')
    list_filter = ('is_active', 'enrollment_date')
    search_fields = ('student_id', 'full_name', 'email')
    ordering = ('student_id',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'time_limit', 'created_by', 'created_at', 'due_date', 'is_active')
    list_filter = ('difficulty', 'is_active', 'created_at', 'due_date')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'task', 'status', 'submitted_at', 'time_taken', 'score')
    list_filter = ('status', 'language', 'submitted_at')
    search_fields = ('student__full_name', 'task__title')
    ordering = ('-submitted_at',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'created_at')
    list_filter = ('user_type', 'created_at')
    search_fields = ('user__username', 'user__email')

# Register models
admin.site.register(Student, StudentAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskSubmission, TaskSubmissionAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
