from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', label_suffix=':')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль', label_suffix=':')


class RegisterForm(UserCreationForm):
    name = forms.CharField()
    surname = forms.CharField()
    role = forms.ChoiceField(choices=[(0, 'Ученик'), (1, 'Учитель')])
    city = forms.CharField()
    organization = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'surname', 'role', 'city', 'organization')
