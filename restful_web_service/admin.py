# Register your models here.
from django.contrib import admin

import restful_web_service.models as models

admin.site.register(models.SystemGroup)
admin.site.register(models.SystemPart)

admin.site.register(models.TaskGroup)
admin.site.register(models.TaskLeaf)

admin.site.register(models.Division)
admin.site.register(models.Employee)
admin.site.register(models.Position)

admin.site.register(models.Artefact)
