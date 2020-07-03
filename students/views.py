import json
import logging
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from marengue import calendarpython
from students import lesson_sync

from . import forms
from .models import District, Lesson, Level, Money, Price, Source, Student

googleCal = calendarpython.MarengueCal()

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def index(request):
    students = Student.objects.order_by('second_name')
    paginator = Paginator(students, 2) # Show 25 contacts per page.
    page_number = request.GET.get('page')

    context = {
        'students': students,
        'page_obj': paginator.get_page(page_number),
    }
    return render(request, 'students/index.html', context)


@login_required
def student_detail_view(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    lessons = student.lessons.filter(status=1).order_by('-date')
    dflt = student.default_lesson_time
    if student.default_lesson_time is None:
        dflt = 60

    tariff_main = student.tarif_live() * dflt
    tariff_skype = student.tarif_skype() * dflt

    balance = student.balance()

    len_lesson = lessons.count()
    sum_lesson = sum(lesson.lesson_long for lesson in lessons)
    cancels = student.lessons.filter(status=2)
    income = sum(lesson.cost() for lesson in lessons)
    lost = sum(lesson.cost() for lesson in cancels)

    context = {
        'student': student,
        'lessons': lessons,
        'len_lesson': len_lesson,
        'sum_lesson': sum_lesson,
        'cancels': cancels.count(),
        'tariff_main': tariff_main,
        'tariff_skype': tariff_skype,
        'income': income,
        'lost': lost,
        'dflt': dflt,
        'balance': balance,

    }

    return render(request, 'students/student_detail.html', context)


@login_required
def settings_view(request, option=None):
    level = Level.objects.order_by('rank')
    district = District.objects.order_by('district_name')
    source = Source.objects.order_by('source_name')
    forms_set = {
        'source': forms.SourceForm,
        'level': forms.LevelForm,
        'district': forms.DistrictForm
    }

    if request.method == 'POST':

        form = forms_set[option](request.POST)

        if form.is_valid():
            form.save()
            return redirect('students:settings')
        else:
            logger.info("Form invalid")
            return HttpResponse(json.dumps(form.errors))

    context = {
        'forms_set': forms_set,
        'district': district,
        'level': level,
        'source': source,
    }

    return render(request, 'students/settings.html', context)


@login_required
def subject_action_view(request, subject, action, subj_id=None, student_id=None, from_settings=False):

    class Subj:
        subject_set = {
            'student': [forms.StudentForm, Student, None],
            'lesson': [forms.LessonForm, Lesson, {'student': student_id, 'date': datetime.today()}],
            'price': [forms.PriceForm, Price, {'student': student_id, 'start_date': date.today()}],
            'money': [forms.MoneyForm, Money, {'student': student_id, 'start_date': date.today()}],
            'level': [forms.LevelForm, Level, None],
            'district': [forms.DistrictForm, District, None],
            'source': [forms.SourceForm, Source, None],
        }

        def __init__(self, subject):
            self.form = self.subject_set[subject][0]
            self.model = self.subject_set[subject][1]
            self.init = self.subject_set[subject][2]

    subj = Subj(subject)

    if student_id:
        redirect_ = redirect('students:detail', student_id=student_id)
    elif from_settings:
        redirect_ = redirect('students:settings',)
    elif subject == 'student' and action == 'edit':
        redirect_ = redirect('students:detail', student_id=subj_id)
    else:
        redirect_ = redirect('students:index',)

    del_button = False
    subj_instance = None
    if subj_id is not None: subj_instance = get_object_or_404(subj.model, pk=subj_id)

    if action == 'delete':
        if request.method == 'POST':
            obj = get_object_or_404(subj.model, pk=subj_id)
            obj.delete()
            return redirect_
        del_button = 'warning'
        form = get_object_or_404(subj.model, pk=subj_id)

    if request.method == 'POST':
        form = subj.form(request.POST, instance=subj_instance)

        if form.is_valid():
            form.save()
            return redirect_
        else:
            logger.info("Form invalid")
            return HttpResponse(json.dumps(form.errors))

    if action == 'add':
        form = subj.form(initial=subj.init)

    if action == 'edit':
        form = subj.form(instance=subj_instance)
        del_button = 'show'

    context = {
        'form': form,
        'subject': subject,
        'subj_id': subj_id,
        'student_id': student_id,
        'action': action,
        'del_button': del_button,
    }

    return render(request, 'students/action_form.html', context)


class ContactView(LoginRequiredMixin, FormView):
    template_name = 'students/contacts.html'
    form_class = forms.ContactForm
    success_url = '..'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super().form_valid(form)


@login_required
def google_cal_refresh(request):
    googleCal.take_all_events()
    return redirect('students:lessons')


@login_required
def google_cal_sync(request):
    lesson_sync.sync_event_and_lesson_through_token()
    return redirect('students:lessons')


@login_required
def student_lessons(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    lessons = student.lessons.order_by('-date')

    context = {
        'student': student,
        'lessons': lessons,
    }
    return render(request, 'students/student_lessons.html', context)

@login_required
def student_prices(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    prices = student.prices.order_by('-start_date')

    context = {
        'student': student,
        'prices': prices,
    }
    return render(request, 'students/student_prices.html', context)

@login_required
def student_payments(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    payments = student.payments.order_by('-date')

    context = {
        'student': student,
        'payments': payments,
    }
    return render(request, 'students/student_payments.html', context)


class StudentsListView(LoginRequiredMixin, ListView):
    model = Student
    paginate_by = 20


class LessonsListView(LoginRequiredMixin, ListView):

    model = Lesson
    paginate_by = 20  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['sync_elements'] = googleCal.marengue_sync_elements()
        context['events'] = googleCal.marengue_all_events_list()
        return context
