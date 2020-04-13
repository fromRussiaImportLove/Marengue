from django.urls import path, re_path
from . import views



app_name = 'students'
urlpatterns = [
    path('', views.index, name='index'),
    path('contacts/', views.ContactView.as_view(), name='contacts'),
    path('lessons/', views.LessonsListView.as_view(), name='lessons'),
    path('settings/', views.settings_view, name='settings'),
    re_path(r'^student/(?P<student_id>\d+)/$', views.student_detail, name='detail'),
    re_path(r'^student/(?P<student_id>\d+)/(?P<subject>\w+)/(?P<action>\w+)(?:/(?P<subj_id>\d+))?/$',
            views.subject_action, name='student_subj_action'),
    re_path(r'^(?P<subject>\w+)/(?P<action>\w+)(?:/(?P<subj_id>\d+))?(?:/(?P<from_settings>\d))?/$',
            views.subject_action, name='subj_action'),
    ]
