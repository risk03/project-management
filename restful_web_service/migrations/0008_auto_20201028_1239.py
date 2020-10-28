# Generated by Django 3.1.2 on 2020-10-28 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restful_web_service', '0007_auto_20201028_1231'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='name',
            new_name='full_name',
        ),
        migrations.AddField(
            model_name='employee',
            name='short_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
