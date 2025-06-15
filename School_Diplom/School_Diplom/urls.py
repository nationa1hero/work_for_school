from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path

from .settings import dev
from backend.views import *

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', log, name='log'),
    path('', home, name='home'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('tasks/', tasks, name='tasks'),
    path('items/', items, name='items'),
    path('items_olymp/', items_olymp, name='items_olymp'),
    path('items_olymp/chose_task_olymp/', chose_task_olymp, name='chose_task_olymp'),
    path('task/', task, name='task'),
    path('export/', export_task_results, name='export_task_results'),

]

if dev.DEBUG:
    urlpatterns += static(dev.MEDIA_URL, document_root=dev.MEDIA_ROOT)