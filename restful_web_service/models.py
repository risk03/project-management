from django.db import models


# Create your models here.
class TaskComponent(models.Model):
    parent = models.ForeignKey("TaskGroup", null=True, blank=True, on_delete=models.CASCADE, related_name='child')
    name = models.CharField(max_length=255, null=False)
    creator = models.ForeignKey("Employee", null=False, on_delete=models.CASCADE, related_name='creation')
    responsible = models.ForeignKey("Employee", null=False, on_delete=models.CASCADE, related_name='resonsibility')

    def __str__(self):
        return self.name


class TaskLeaf(TaskComponent):
    start = models.DateTimeField()
    end = models.DateTimeField()


class Artefact(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=1024, null=True)
    task = models.ForeignKey("TaskLeaf", null=False, on_delete=models.CASCADE, related_name="artefact")

    def __str__(self):
        return self.title + ' - ' + self.task.name


class TaskGroup(TaskComponent):
    pass


class TaskSequence(models.Model):
    previous = models.ForeignKey("TaskLeaf", null=False, blank=False, on_delete=models.CASCADE, related_name='next')
    next = models.ForeignKey("TaskLeaf", null=False, blank=False, on_delete=models.CASCADE, related_name='previous')

    def __str__(self):
        return self.previous.name + " -> " + self.next.name


class StructureComponent(models.Model):
    parent = models.ForeignKey("Division", null=True, blank=True, on_delete=models.SET_NULL, related_name="child")


class Division(StructureComponent):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name


class Employee(StructureComponent):
    full_name = models.CharField(max_length=255, null=False)
    short_name = models.CharField(max_length=255, null=True)
    position = models.ForeignKey("Position", null=True, blank=True, on_delete=models.SET_NULL)
    login = models.CharField(max_length=32, null=True, unique=True)
    salt = models.CharField(max_length=32, null=True)
    hash = models.CharField(max_length=32, null=True)
    isadmin = models.BooleanField(null=False, default=False)

    def __str__(self):
        return (self.short_name if self.short_name else self.full_name) + ', ' + self.position.name


class Position(models.Model):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name

class SystemComponent(models.Model):
    name = models.CharField(max_length=255, null=False)
    parent = models.ForeignKey("SystemGroup", null=True, blank=True, on_delete=models.CASCADE, related_name="child")

    def __str__(self):
        return self.name


class SystemGroup(SystemComponent):
    pass


class SystemPart(SystemComponent):
    pass
