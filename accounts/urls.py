from django.urls import path, re_path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.AccLogin.as_view(), name='login'),
    path('profile/', views.acc_profile, name='profile'),
    path('profile/change/', views.ChangeUserInfoView.as_view(), name='profile_change'),
    path('logout/', views.AccLogout.as_view(), name='logout',),
    path('password/change/', views.AccPasswordChangeView.as_view(), name='password_change')
    ]
