from django.urls import path, re_path
from . import views


app_name = 'students'
urlpatterns = [
    path('', views.index, name='index'),
    path('contacts/', views.ContactView.as_view(), name='contacts'),
    path('students/', views.StudentsListView.as_view(), name='students'),
    path('lessons/', views.LessonsListView.as_view(), name='lessons'),
    path('lessons/cal_refresh', views.google_cal_refresh, name='googlecal_refresh'),
    path('lessons/cal_sync', views.google_cal_sync, name='googlecal_sync'),
    re_path(r'^settings/(?P<option>\w+)?$', views.settings_view, name='settings'),
    re_path(r'^student/(?P<student_id>\d+)/$', views.student_detail_view, name='detail'),
    re_path(r'^student/(?P<student_id>\d+)/lessons/$', views.student_lessons, name='student_lessons'),
    re_path(r'^student/(?P<student_id>\d+)/prices/$', views.student_prices, name='student_prices'),
    re_path(r'^student/(?P<student_id>\d+)/payments/$', views.student_payments, name='student_payments'),
    re_path(r'^student/(?P<student_id>\d+)/(?P<subject>\w+)/(?P<action>\w+)(?:/(?P<subj_id>\d+))?/$',
            views.subject_action_view, name='student_subj_action'),
    re_path(r'^(?P<subject>\w+)/(?P<action>\w+)(?:/(?P<subj_id>\d+))?(?:/(?P<from_settings>\d))?/$',
            views.subject_action_view, name='subj_action'),
    ]
