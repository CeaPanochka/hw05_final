from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(label='Текущий пароль')
    new_password = forms.CharField(label='Новый пароль')
    repeat_new_password = forms.CharField(label='Повтор нового пароля')
