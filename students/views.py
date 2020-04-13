from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect, reverse
from . import forms
from .models import Student, Price, Lesson, District, Level, Money
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, datetime

# from django.urls import reverse
import json
import logging

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


# Create your views here.

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    #    price = get_list_or_404(Price.objects.order_by('-start_date'), student=student_id)
    #    lesson = get_list_or_404(Lesson.objects.order_by('-date'), student=student_id)

    prices = Price.objects.filter(student_id=student_id).order_by('-start_date')
    lessons = Lesson.objects.filter(student_id=student_id).order_by('-date')

    price_error = False
    price_lesson = {}
    for lesson in lessons:
        actual_tariff = set()
        for price in prices:
            if lesson.date.date() >= price.start_date:
                actual_tariff.add(price.start_date)
        if actual_tariff != set():
            price_lesson[lesson.date] = prices.filter(start_date=max(actual_tariff))[0].tariff() \
                                        * lesson.lesson_long // 60
        else:
            price_lesson[lesson.date] = 'Warn! Lesson without setting price!!!'
            price_error = True

    if price_error:
        sum_price = 'Can\'t count, couse some lesson don\'t have price!'
    else:
        sum_price = sum(price_lesson.values())

    context = {
        'student': student,
        'birthday': student.birthday,
        'district': student.district,
        'price': prices,
        'lessons': lessons,
        'price_lesson': price_lesson,
        'sum_price': sum_price
    }
    return render(request, 'students/student_detail.html', context)

@login_required
def del_object(_model, subj_id):
    obj = get_object_or_404(_model, pk=subj_id)
    obj.delete()
#    return redirect('students:index')

@login_required
def settings_view(request):
    level = Level.objects.order_by('rank')
    district = District.objects.order_by('district_name')

    if request.method == 'POST':
        form = forms.LevelForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('students:settings')
        else:
            logger.info("Form invalid")
            return HttpResponse(json.dumps(form.errors))

    context = {
        'LevelForm': forms.LevelForm,
        'DistrictForm': forms.DistrictForm,
        'district': district,
        'level': level
    }

    return render(request, 'students/settings.html', context)


@login_required
def subject_action(request, subject, action, subj_id=False, student_id=None, from_settings=False):
    _forms = {
        'student': forms.StudentForm,
        'lesson': forms.LessonForm,
        'price': forms.PriceForm,
        'level': forms.LevelForm,
        'district': forms.DistrictForm,
        'money': forms.MoneyForm
    }

    _models = {
        'student': Student,
        'lesson': Lesson,
        'price': Price,
        'district': District,
        'level': Level,
        'money': Money
    }

    _initial = {
        'student': None,
        'lesson': {'student': student_id, 'date': datetime.today()},
        'price': {'student': student_id, 'start_date': date.today()},
        'district': None,
        'level': None,
        'money': {'student': student_id, 'start_date': date.today()},
    }

    subj_instance = None
    if subj_id: subj_instance = _models[subject].objects.get(pk=subj_id)

    if request.method == 'POST':
        form = _forms[subject](request.POST, instance=subj_instance)

        if form.is_valid():
            form.save()
            if from_settings: return redirect('students:settings')
            if student_id: return redirect('students:detail', student_id=student_id)
            return redirect('students:index')  # TODO make success redirect, may be request.referer

            # ('students:student_add', args=[submitted])
            # #HttpResponseRedirect(reverse('students:student_add')) /
        else:
            logger.info("Form invalid")
            return HttpResponse(json.dumps(form.errors))

    if action == 'add':
        form = _forms[subject](initial=_initial[subject])

    if action == 'edit':
        form = _forms[subject](instance=subj_instance)

    if action == 'delete':
        obj = get_object_or_404(_models[subject], pk=subj_id)
        obj.delete()
        if student_id and subject != 'student': return redirect('students:detail', student_id=student_id)
        return redirect('students:index')

    context = {
        'form': form,
        'subject': subject,
        'action': action,
        'submitted': False,
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


class LessonsListView(LoginRequiredMixin, ListView):

    model = Lesson
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
