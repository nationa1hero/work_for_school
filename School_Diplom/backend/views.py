import base64

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from openpyxl import Workbook
from openpyxl.styles import Alignment

from .forms import RegistrationForm, LoginForm, TaskAnswerForm, ProfileForm, StudentSelectForm
from .models import *
from .utils import assign_tasks_to_student

ARRAY_DATA_CONST = [4.5, 6.75, 10.125, 15.1875, 22.78125, 34.171875, 51.2578125, 76.88671875, 115.330078125]
ARRAY_SUM = 336.990234375
COEFFICIENT = 30


def export_task_results(request):
    if request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            form = StudentSelectForm(request.POST)
            if form.is_valid():
                student = form.cleaned_data['student']

                if student == 'all':
                    task_results = TaskResult.objects.all().order_by('student')
                    file_name = 'all'
                else:
                    student = Student.objects.get(id=student)
                    task_results = TaskResult.objects.filter(student=student)
                    file_name = f'{student.profile_data.login}'

                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = f'attachment; filename="task_results_{file_name}.xlsx"'

                wb = Workbook()
                ws = wb.active
                ws.title = "Результаты задач"

                headers = ["Задачи", "Ученик", "Верно/Не верно", "Дата отправки задачи"]
                ws.append(headers)
                ws.column_dimensions['A'].width = 11
                ws.column_dimensions['B'].width = 11
                ws.column_dimensions['C'].width = 30
                ws.column_dimensions['D'].width = 40

                for result in task_results:
                    if result.result:
                        res = 'Верно'
                    else:
                        res = 'Не верно'
                    completion_date_formatted = result.completion_date.replace(tzinfo=None).strftime('%d.%m.%Y-%H:%M:%S')
                    ws.append([result.task.id, result.student.profile_data.name, res, completion_date_formatted])

                # Центрируем содержимое всех столбцов
                for row in ws.iter_rows():
                    for cell in row:
                        cell.alignment = Alignment(horizontal='center', vertical='center')

                # Перемещаем указатель на начало буфера после изменений
                wb.save(response)
                return response
            else:
                return render(request, 'html/export_task_results.html', {'form': form})
        else:
            form = StudentSelectForm()
            return render(request, 'html/export_task_results.html', {'form': form})
    else:
        return redirect('home')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                login = form.cleaned_data.get('login')
                clazz = form.cleaned_data.get('clazz')
                name = form.cleaned_data.get('name')
                password = form.cleaned_data.get('password')
                password2 = form.cleaned_data.get('password2')
                if password and password2:
                    if password != password2:
                        raise ValidationError('Пароли не совпадают')
                user = ProfileData.objects.create_user(login=login, clazz=clazz, name=name, password=password)
                student = Student.objects.create(profile_data=user, clazz=user.clazz)
                assign_tasks_to_student(student)
                return redirect('login')
            except Exception as e:
                # В случае возникновения ошибки при сохранении пользователя,
                # отобразим сообщение об ошибке и форму регистрации снова.
                error_message = e
                return render(request, 'html/registration.html', {'form': form, 'error_message': error_message})
    else:
        form = RegistrationForm()
    return render(request, 'html/registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            user = authenticate(request, login=username, password=password)
            if user is not None:
                login(request, user)
                # Пользователь успешно аутентифицирован
                if request.user.is_authenticated:
                    return redirect('home')  # Перенаправляем на главную страницу после входа
            else:
                # Неверные учетные данные
                return render(request, 'html/login.html',
                              {'form': form, 'error_message': 'Неверное имя пользователя или пароль.'})
    else:
        form = LoginForm()
    return render(request, 'html/login.html', {'form': form})


@login_required
def home(request):
    user = ProfileData.objects.get(pk=request.user.id)
    if user.is_staff and user.is_superuser:
        students = Student.objects.all()
        return render(request, 'html/admin_account.html', {'user': user, 'students': students})
    student = Student.objects.get(profile_data=user)
    points = student.points
    student_rank = student.rank
    if student_rank == 1:
        score_up = ARRAY_DATA_CONST[student_rank-1] * COEFFICIENT
        percent_points = round(points / score_up * 100, 2)
    elif student_rank != 10:
        score_down = ARRAY_DATA_CONST[student_rank-2] * COEFFICIENT
        score_up = ARRAY_DATA_CONST[student_rank-1] * COEFFICIENT
        score = score_up - score_down
        point = points - score_down
        percent_points = round(point / score * 100, 2)
    else:
        score_down = ARRAY_DATA_CONST[student_rank-2] * COEFFICIENT
        score = score_down
        point = points - score_down
        percent_points = round(point / score * 100, 2)
    achievements_general = Achievement.objects.filter(student=student, scale=0)
    achievements_inside = Achievement.objects.filter(student=student, scale=1)
    task_complete = TaskResult.objects.filter(student=student, result=True).count()
    size_task_resolved = TaskResult.objects.filter(student=student).count()
    if task_complete != 0:
        percent_true_tasks_size = task_complete / size_task_resolved * 100
        percent_true_tasks_size = int(percent_true_tasks_size)
    else:
        percent_true_tasks_size = 0
    return render(request, 'html/account.html', {
        'user': user,
        'student_rank': student_rank,
        'point': points,
        'percent_point': percent_points,
        'achievements_general': achievements_general,
        'achievements_inside': achievements_inside,
        'size_task':size_task_resolved,
        'percent_true_tasks_size': percent_true_tasks_size
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            cropped_image_data = form.cleaned_data.get('cropped_image')

            if cropped_image_data:
                format, imgstr = cropped_image_data.split(';base64,')
                ext = format.split('/')[-1]
                filename = f'{request.user.id}_avatar.{ext}'
                profile_image = ContentFile(base64.b64decode(imgstr), name=filename)
                profile.profile_picture = profile_image

            profile.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'html/edit_profile.html', {'form': form})


def log(request):
    logout(request)
    return redirect('login')


@login_required
def tasks(request):
    students_rating = []
    top_ten_rating = True
    user_auth = Student.objects.get(profile_data=request.user.id)
    students = Student.objects.all().order_by('-points')
    for index, student in enumerate(students):
        students_rating.append(
            {
                'student': student,
                'index': index + 1
            }
        )
        if student.id == user_auth.id:
            rating_student = index + 1

    if rating_student > 10:
        students_rating = students_rating[:10]
    else:
        students_rating = students_rating[:11]
        top_ten_rating = False
    return render(request, 'html/tasks.html', {'students': students_rating, 'user': user_auth,
                                               'index': rating_student, 'top_ten_rating': top_ten_rating})


@login_required
def items(request):
    items_list = list(Subject.objects.all())
    items = list()
    for item in items_list:
        items.append(item.subject.lower())
    return render(request, 'html/items.html', {'items': items})


@login_required
def items_olymp(request):
    items_list = list(Subject.objects.all())
    items = list()
    for item in items_list:
        items.append(item.subject.lower())
    return render(request, 'html/items_olymp.html', {'items': items})


@login_required
def chose_task_olymp(request):
    return render(request, 'html/chose_task_olymp.html')


@login_required
def task(request):
    tasks = Task.objects.all()
    sum_points = 0
    for task in tasks:
        sum_points += task.number_of_points
    score_point = ARRAY_SUM / sum_points

    user = request.user
    student = get_object_or_404(Student, profile_data=user)
    size_resolved_task_general = TaskResult.objects.filter(student=student).count()
    index = student.current_task_index
    assigned_tasks = AssignedTask.objects.filter(student=student).order_by('current_task_index')
    size_resolved_task_math = TaskResult.objects.filter(student=student, subject=1).count()
    assigned_task = assigned_tasks[index]
    current_task = assigned_tasks[index].task

    rank_student = student.rank
    score_up = 0
    if rank_student != 10:
        score_up = ARRAY_DATA_CONST[rank_student-1] * COEFFICIENT

    if request.method == 'POST':
        form = TaskAnswerForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer']
            result = current_task.answer == answer

            if result:
                student.points += current_task.number_of_points * score_point * COEFFICIENT
                if score_up <= student.points:
                    student.rank += 1
                student.save()

            TaskResult.objects.create(student=student, task=current_task,
                                      result=result, completion_date=now(), subject=current_task.subject)
            assigned_task.completed_at = now()
            assigned_task.save()

            check_achievements(student, size_resolved_task_general, size_resolved_task_math)
            if index == 6:
                student.current_task_index = 0
                student.save()
                assign_tasks_to_student(student)
                return redirect('home')
            else:
                student.current_task_index += 1
                student.save()
                task = assigned_tasks[index + 1].task
            return render(request, 'html/task.html', {'task': task,
                                                      'index': student.current_task_index,
                                                      'i': student.current_task_index + 1},)

    return render(request, 'html/task.html', {'task': current_task,
                                              'index': student.current_task_index,
                                              'i': student.current_task_index + 1})


def check_achievements(student, size_resolved_task_general, size_resolved_task_math):
    size_all_task_math = Task.objects.filter(subject=1).count()
    if student.current_task_index == 1:
        Achievement.objects.get_or_create(student=student, text='Так держать!', scale=0, description='Решил первые 2 задачи на платформе')
    if size_resolved_task_general >= 10:
        Achievement.objects.get_or_create(student=student, text='Начинающий решатель!', scale=0, description='Решить первые 10 задач на платформе')
    if size_resolved_task_general >= 50:
        Achievement.objects.get_or_create(student=student, text='Стремящийся ученик!', scale=0, description='Решить 50 задач на платформе')
    if size_resolved_task_general >= 100:
        Achievement.objects.get_or_create(student=student, text='Заслуженный ученик!', scale=0, description='Решить 100 задач на платформе')
    if size_resolved_task_general >= 200:
        Achievement.objects.get_or_create(student=student, text='Гений решений!', scale=0, description='Решить 200 задач на платформе')
    if size_resolved_task_general >= 500:
        Achievement.objects.get_or_create(student=student, text='Непревзойденный интеллект!', scale=0, description='Решить 500 задач на платформе')
    if size_resolved_task_math >= 20:
        Achievement.objects.get_or_create(student=student, text='Математический новичок!', scale=1, description='Решить 20 задач по математике')
    if size_resolved_task_math >= 50:
        Achievement.objects.get_or_create(student=student, text='Математический искатель!', scale=1, description='Решить 50 задач по математике')
    if size_resolved_task_math >= 100:
        Achievement.objects.get_or_create(student=student, text='Математический мастер!', scale=1, description='Решить 100 задач по математике')
    if size_all_task_math == size_resolved_task_math:
        Achievement.objects.get_or_create(student=student, text='Гуру математики!', scale=1, description='Решить все задачи по математике')
    if student.rank == 2:
        Achievement.objects.get_or_create(student=student, text='Продвигающийся ученик!', scale=0, description='Получить второй ранг в любом предмете')
    if student.rank == 3:
        Achievement.objects.get_or_create(student=student, text='Уверенный знаток!', scale=0, description='Получить третий ранг в любом предмете')
    if student.rank == 4:
        Achievement.objects.get_or_create(student=student, text='Настоящий исследователь!', scale=0, description='Получить четвертый ранг в любом предмете')
    if student.rank == 5:
        Achievement.objects.get_or_create(student=student, text='Заслуженный эксперт!', scale=0, description='Получить пятый ранг в любом предмете')
    if student.rank == 6:
        Achievement.objects.get_or_create(student=student, text='Продвинутый мастер!', scale=0, description='Получить шестой ранг в любом предмете')
    if student.rank == 7:
        Achievement.objects.get_or_create(student=student, text='Выдающийся ученый!', scale=0, description='Получить седьмой ранг в любом предмете')
    if student.rank == 8:
        Achievement.objects.get_or_create(student=student, text='Элита знаний!', scale=0, description='Получить восьмой ранг в любом предмете')
    if student.rank == 9:
        Achievement.objects.get_or_create(student=student, text='Непревзойденный ум!', scale=0, description='Получить девятый ранг в любом предмете')
    if student.rank == 10:
        Achievement.objects.get_or_create(student=student, text='Вершина мастерства!', scale=0, description='Получить десятый ранг в любом предмете')
