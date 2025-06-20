# Generated by Django 5.0.6 on 2024-06-24 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_achievement_scale'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('coefficient', models.FloatField()),
            ],
            options={
                'verbose_name': 'Ранг',
                'verbose_name_plural': 'Ранги',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='image_id',
            field=models.ImageField(default=1, upload_to='task_image/'),
            preserve_default=False,
        ),
    ]
