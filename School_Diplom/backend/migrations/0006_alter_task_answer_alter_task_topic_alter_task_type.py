# Generated by Django 5.0.6 on 2024-05-22 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_rename_profile_data_id_student_profile_data_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='answer',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='task',
            name='topic',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='task',
            name='type',
            field=models.CharField(max_length=100),
        ),
    ]
