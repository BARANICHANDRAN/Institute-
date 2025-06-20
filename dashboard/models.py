from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    COURSE_CHOICES = [
        ('FS', 'Full Stack'),
        ('JAVA', 'JAVA'),
        ('PY', 'Python'),
        ('TEST', 'Testing'),
        ('CC', 'Cloud Computing'),
        ('AI', 'Artificial Intelligence'),
    ]
    course = models.CharField(max_length=20, choices=COURSE_CHOICES, default='bca')
    enrollment_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.student_id} - {self.full_name}"

class Task(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    problem_statement = models.TextField()
    sample_input = models.TextField(blank=True, null=True)
    sample_output = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    time_limit = models.IntegerField(default=60, help_text='Time limit in minutes')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class TaskSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20, default='python')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_taken = models.IntegerField(blank=True, null=True, help_text='Time taken in seconds')
    score = models.IntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'task']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.task.title}"

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
