from django import forms
from django.contrib.auth.models import User
from .models import AdvUser


class ChangeAdvUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='e-mail address')

    class Meta:
        model = AdvUser
        fields = '__all__'


class ChangeUserInfoForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'
