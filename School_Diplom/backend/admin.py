from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse, path

from .models import Student, ProfileData, Subject, TaskResult, Task, AssignedTask, Achievement, Rank
from .views import export_task_results


class TaskResultAdmin(admin.ModelAdmin):
    change_list_template = 'admin/task_result_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export_task_results/', self.admin_site.admin_view(export_task_results), name='export_task_results'),
        ]
        return custom_urls + urls


    def export_task_results_view(self, request):
        return HttpResponseRedirect(reverse('export_task_results'))


admin.site.register(TaskResult, TaskResultAdmin)
admin.site.register(Achievement)
admin.site.register(Student)
admin.site.register(ProfileData)
admin.site.register(Subject)
admin.site.register(Task)
admin.site.register(AssignedTask)
admin.site.register(Rank)
