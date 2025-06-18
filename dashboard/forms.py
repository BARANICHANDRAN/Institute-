from django import forms
from .models import Student, Task

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'full_name', 'email', 'phone', 'date_of_birth', 'address']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'problem_statement', 'sample_input', 'sample_output', 'difficulty', 'time_limit', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'problem_statement': forms.Textarea(attrs={'rows': 5}),
            'sample_input': forms.Textarea(attrs={'rows': 3}),
            'sample_output': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        } 