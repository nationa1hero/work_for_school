from celery import shared_task
from .models import AssignedTask, Task, Student, TaskResult


def assign_tasks_to_student(student):
    # Получить все решенные задачи
    task_results = TaskResult.objects.filter(student=student)
    solved_task_ids = task_results.values_list('task_id', flat=True)
    incorrect_task_ids = task_results.filter(result=False).values_list('task_id', flat=True)

    # Функция для выдачи задач заданного уровня
    def assign_tasks_of_level(level, student):
        # Удалить старые задачи
        AssignedTask.objects.filter(student=student).delete()

        tasks = Task.objects.filter(level=level).order_by('?').exclude(id__in=solved_task_ids).exclude(
            id__in=incorrect_task_ids)[:7]
        index = 0
        for task in tasks:
            AssignedTask.objects.create(student=student, task=task, current_task_index=index)
            index += 1
        return len(tasks)  # Возвращаем количество выданных задач

    # Начнем с задач первого уровня и будем двигаться вверх
    level = 1
    while True:
        tasks_assigned = assign_tasks_of_level(level, student)
        if tasks_assigned < 7 and level != 4:
            level += 1
        else:
            level -= 1
            break

    # Если все задачи всех уровней выданы, выдать задачи, которые были решены неправильно
    if level == 3:
        tasks = Task.objects.filter(id__in=incorrect_task_ids).exclude(id__in=solved_task_ids)[:7]
        if len(tasks) < 7:
            tasks = Task.objects.order_by('?')[:7]
        index = 0
        for task in tasks:
            AssignedTask.objects.create(student=student, task=task, current_task_index=index)
            index += 1


@shared_task
def assign_tasks_to_students():
    students = Student.objects.all()
    for student in students:
        assign_tasks_to_student(student)
