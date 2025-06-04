from django import forms
from PIL import Image
from .models import ProfileData, TaskResult, Student


class RegistrationForm(forms.ModelForm):
    name = forms.CharField(label='Имя', max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}))
    clazz = forms.CharField(label='Класс',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите класс'}),
                            max_length=3)
    login = forms.CharField(label='Логин', max_length=100,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'}))
    password = forms.CharField(label='Пароль', max_length=100, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(label='Подтвердите пароль', max_length=100, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}))

    class Meta:
        model = ProfileData
        fields = ['name', 'clazz', 'login', 'password', 'password2']


class LoginForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=100,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'}))
    password = forms.CharField(label='Пароль', max_length=100,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))

    class Meta:
        model = ProfileData
        fields = ['login', 'password']


class TaskAnswerForm(forms.Form):
    answer = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите ваш ответ'
    }))

    class Meta:
        model = TaskResult
        fields = ['answer']


class ProfileForm(forms.ModelForm):
    cropped_image = forms.CharField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(label='Имя', max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}))

    class Meta:
        model = ProfileData
        fields = ['name']


class StudentSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StudentSelectForm, self).__init__(*args, **kwargs)
        self.fields['student'].choices = ([('all', 'Все Ученики')]
                                          + [(student.id, student.profile_data.name) for student in
                                             Student.objects.all()])

    student = forms.ChoiceField(choices=[], required=True, label="Выберите студента")

    class Meta:
        model = Student
        fields = ['student']
