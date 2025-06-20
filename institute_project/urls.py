from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.contrib.auth import logout
from django.conf import settings
from django.conf.urls.static import static

def custom_logout(request):
    """Custom logout view that accepts GET requests"""
    logout(request)
    return redirect('login')

def redirect_to_login(request):
    """Redirect root URL to login page"""
    return redirect('login')

urlpatterns = [
    # Root URL - redirects to login
    path('', redirect_to_login, name='home'),
    
    # Django Admin Interface
    path('django-admin/', admin.site.urls, name='django_admin'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', custom_logout, name='logout'),
    
    # Institute Dashboard URLs
    path('institute/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
