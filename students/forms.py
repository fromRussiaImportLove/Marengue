from django import forms
from .models import Student, Lesson, District, Price, CHOICES_GENDER
from django.utils.translation import gettext_lazy as _



class StudentAddForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='First name of student')
    second_name = forms.CharField(max_length=30, label='Second name of student')
    #gender = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'radio-control'}), choices=CHOICES_GENDER, initial='man'),
    gender = forms.CharField(widget=forms.RadioSelect(choices=CHOICES_GENDER), initial='man'),
    #birthday = forms.DateField(required=False, help_text='MM/DD/YYYY', widget=forms.SelectDateWidget)
    birthday = forms.DateField(
         label=_('Date of birth'),
         help_text='DD-MM-YYYY',
         input_formats=('%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'))

    district = forms.ModelChoiceField(queryset=District.objects.all())
    source = forms.CharField(widget=forms.Textarea, required=False, label="Origin of opportunity")

    class Meta:
        model = Student
        fields = '__all__'
        '''widgets = {
            'gender': forms.RadioSelect(choices=CHOICES_GENDER)
        }'''


class LessonAddForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), label='Student')
    date = forms.DateField(help_text='MM/DD/YYYY', widget=forms.SelectDateWidget)
    lesson_long = forms.IntegerField(min_value=1, label='Amount minutes for lesson', initial=60)

    class Meta:
        model = Lesson
        fields = ['student', 'date', 'lesson_long']
        labels = {'student': _('Select Student'), }
        help_texts = {'student': _('With who you lesson'), }


class PriceAddForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), label='Student')
    start_date = forms.DateField(help_text='MM/DD/YYYY', widget=forms.SelectDateWidget)  # TODO can make select old date
    cost = forms.IntegerField(min_value=0, label='Price', help_text='How much for lesson pay', initial=0)
    duration = forms.IntegerField(min_value=1, label='Amount minutes for lesson', initial=60)

    class Meta:
        model = Price
        fields = ['student', 'start_date', 'cost', 'duration']


class ContactForm(forms.Form):
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
