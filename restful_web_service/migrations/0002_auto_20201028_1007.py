# Generated by Django 3.1.2 on 2020-10-28 07:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restful_web_service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.DeleteModel(
            name='Value',
        ),
        migrations.CreateModel(
            name='TaskLeaf',
            fields=[
                ('taskcomponent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='restful_web_service.taskcomponent')),
            ],
            bases=('restful_web_service.taskcomponent',),
        ),
        migrations.CreateModel(
            name='TaskNode',
            fields=[
                ('taskcomponent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='restful_web_service.taskcomponent')),
            ],
            bases=('restful_web_service.taskcomponent',),
        ),
        migrations.AddField(
            model_name='taskcomponent',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restful_web_service.tasknode'),
        ),
    ]