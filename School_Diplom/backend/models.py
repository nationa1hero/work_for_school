from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, clazz=None, name=None, **extra_fields):
        if not login:
            raise ValueError('Поле логин должно быть заполнено')
        user = self.model(login=login, clazz=clazz, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('clazz', 777)
        return self.create_user(login, password, **extra_fields)


class ProfileData(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=256)
    profile_picture = models.ImageField(upload_to='images/', null=True, blank=True)
    name = models.CharField(max_length=30)
    clazz = models.CharField(max_length=30, null=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"Логин: {self.login} - Имя: {self.name}"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class Subject(models.Model):
    subject = models.TextField()

    def __str__(self):
        return f"{self.subject}"

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    text = models.TextField()
    answer = models.CharField(max_length=256)
    topic = models.CharField(max_length=256)
    type = models.CharField(max_length=256)
    level = models.IntegerField(null=False, default=1)
    number_of_points = models.IntegerField(null=False)
    original_id = models.IntegerField(null=False)
    image_name = models.CharField(null=True, max_length=256)

    def __str__(self):
        return f"Задача №{self.id}"

    class Meta:
        verbose_name = "Задачу"
        verbose_name_plural = "Задачи"


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    profile_data = models.ForeignKey(ProfileData, null=False, on_delete=models.CASCADE)
    rank = models.IntegerField(null=False, default=1)
    points = models.IntegerField(null=False, default=0)
    clazz = models.CharField(max_length=30, null=False)
    current_task_index = models.IntegerField(default=0)  # Индекс текущей задачи

    def __str__(self):
        return f"Ученик №{self.id} - {self.profile_data.name}"

    class Meta:
        verbose_name = "Ученика"
        verbose_name_plural = "Ученики"


class TaskResult(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    result = models.BooleanField(default=False)
    completion_date = models.DateTimeField()

    def __str__(self):
        return f"{self.task} с результатом {self.result}"

    class Meta:
        verbose_name = "Результат задачи"
        verbose_name_plural = "Результаты задач"


class AssignedTask(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_task_index = models.IntegerField(default=0)  # Индекс текущей задачи

    def is_completed(self):
        return self.completed_at is not None

    def __str__(self):
        return f'{self.student.profile_data.name} - {self.task.id}'

    class Meta:
        verbose_name = "Назначенную задачу"
        verbose_name_plural = "Назначенные задачи"


class Achievement(models.Model):
    SCALE_ENUM = (
        (0, 'GENERAL'), # Общие
        (1, 'INSIDE') # Внутри
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    text = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    scale = models.CharField(max_length=12, choices=SCALE_ENUM)

    def __str__(self):
        return f'Достижение - {self.student.profile_data.name}'

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"


class Rank(models.Model):
    rank = models.IntegerField(blank=False) #Ранг
    coefficient = models.FloatField(blank=False) #Коэффициент

    def __str__(self):
        return f'Ранг - {self.rang}'

    class Meta:
        verbose_name = "Ранг"
        verbose_name_plural = "Ранги"
