from django import forms
from .models import Student, Task
from django.utils import timezone

class StudentForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            if not phone.isdigit() or len(phone) != 10:
                raise forms.ValidationError('Phone number must contain exactly 10 digits.')
        return phone
    class Meta:
        model = Student
        fields = ['student_id', 'full_name', 'email', 'phone', 'date_of_birth', 'address', 'course']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class TaskForm(forms.ModelForm):
    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date <= timezone.now():
            raise forms.ValidationError('Due date and time must be in the future.')
        return due_date
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