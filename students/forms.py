from django import forms
from .models import Student, Lesson, District, Price, Level, Money, CHOICES_GENDER, CHOICES_LESSON_STATUS
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import widgets


class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='First name of student')
    second_name = forms.CharField(max_length=30, label='Second name of student')
    gender = forms.IntegerField(widget=forms.RadioSelect(
        choices=CHOICES_GENDER, attrs={'class': 'radio-control'}))
    phone = PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget(), required=False)
    district = forms.ModelChoiceField(queryset=District.objects.all())
    source = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Search'}), required=False, label="Origin of opportunity")

    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'birthday': widgets.AdminDateWidget(),
        }


class LessonForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), label='Student')
    date = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget())
    lesson_long = forms.IntegerField(min_value=1, label='Amount minutes for lesson', initial=60)

    class Meta:
        model = Lesson
        fields = ['student', 'date', 'lesson_long', 'skype', 'status']
        labels = {'student': _('Select Student'), }
        help_texts = {'student': _('With who you lesson'), }
        widgets = {
            'date': widgets.AdminSplitDateTime(),
        }


class PriceForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), label='Student')
    cost = forms.IntegerField(min_value=0, label='Price', help_text='How much for lesson pay', initial=0)
    duration = forms.IntegerField(min_value=1, label='Amount minutes for lesson', initial=60)

    class Meta:
        model = Price
        fields = ['student', 'start_date', 'cost', 'duration']
        widgets = {
            'start_date': widgets.AdminDateWidget(),
        }


class LevelForm(forms.ModelForm):

    class Meta:
        model = Level
        fields = ['level_name', 'rank']


class DistrictForm(forms.ModelForm):

    class Meta:
        model = District
        fields = ['district_name']


class MoneyForm(forms.ModelForm):
    date = forms.DateField(help_text='MM/DD/YYYY', widget=forms.SelectDateWidget)
    start_date = forms.DateField(help_text='MM/DD/YYYY', widget=forms.SelectDateWidget)
    student = forms.ModelChoiceField(queryset=Student.objects.all(), label='Student')

    class Meta:
        model = Money
        fields = '__all__'


class ContactForm(forms.Form):
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
