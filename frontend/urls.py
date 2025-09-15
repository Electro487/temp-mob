from django.urls import path
from frontend import views

app_name = "frontend"

urlpatterns = [
    path('auth/', views.auth_view, name='auth'),
    # add path for password reset if used in template
    # path('password-reset/', views.password_reset_view, name='password_reset'),
]
