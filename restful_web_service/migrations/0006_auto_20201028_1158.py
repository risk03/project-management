# Generated by Django 3.1.2 on 2020-10-28 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restful_web_service', '0005_taskleaf_next'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskleaf',
            name='next',
        ),
        migrations.RemoveField(
            model_name='taskleaf',
            name='previous',
        ),
        migrations.CreateModel(
            name='TaskSequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('next', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='previous', to='restful_web_service.taskleaf')),
                ('previous', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='next', to='restful_web_service.taskleaf')),
            ],
        ),
    ]
