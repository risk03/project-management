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
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    STATUS = (
    ('NEW', 'New'), ('PRO', 'In progress'), ('COM', 'Completed'), ('REJ', 'Rejected'), ('REV', 'Send to revision'))
    status = models.CharField(max_length=3, choices=STATUS)
    system = models.ForeignKey("SystemComponent", null=True, blank=True, related_name='task', on_delete=models.SET_NULL)
    prev = models.ManyToManyField('self', related_name="next", symmetrical=False, blank=True)
    duration = models.DurationField()
    real_early_start = models.DateTimeField(null=True, blank=True)
    real_late_start = models.DateTimeField(null=True, blank=True)
    real_early_end = models.DateTimeField(null=True, blank=True)
    real_late_end = models.DateTimeField(null=True, blank=True)
    prop_early_start = models.DateTimeField(null=True, blank=True)
    prop_late_start = models.DateTimeField(null=True, blank=True)
    prop_early_end = models.DateTimeField(null=True, blank=True)
    prop_late_end = models.DateTimeField(null=True, blank=True)

    @property
    def tei(self):
        if self.prev:
            return max(x.early_end for x in self.prev)
        else:
            return self.early_start
    
    @property
    def tli(self):
        if self.prev:
            return max(x.late_end for x in self.prev)
        else:
            return self.early_start

    @property
    def tej(self):
        if self.next:
            return min(x.early_start for x in self.next)
        else:
            return self.late_end

    @property
    def tlj(self):
        if self.next:
            return min(x.late_start for x in self.next)
        else:
            return self.late_end

    @property
    def event_reserve(self):
        return self.tli - self.tei

    @property
    def full_reserve(self):
        return self.tlj - self.tei - self.duration

    @property
    def free_reserve(self):
        return self.tej - self.tei - self.duration

    @property
    def is_critical(self) -> bool:
        return self.late_start == self.early_start

    @property
    def early_start(self):
        if self.start:
            return self.start
        l = [x for x in [self.real_early_start, self.prop_early_start] if x is not None]
        return max(l) if l else None


    @early_start.setter
    def early_start(self, value):
        self.prop_early_start = value

    @property
    def late_start(self):
        if self.start:
            return self.start
        l = [x for x in [self.real_late_start, self.prop_late_start] if x is not None]
        return min(l) if l else None


    @late_start.setter
    def late_start(self, value):
        self.prop_late_start = value

    @property
    def early_end(self):
        if self.end:
            return self.end
        l = [x for x in [self.real_early_end, self.prop_early_end] if x is not None]
        return max(l) if l else None


    @early_end.setter
    def early_end(self, value):
        self.prop_early_end = value

    @property
    def late_end(self):
        if self.end:
            return self.end
        l = [x for x in [self.real_late_end, self.prop_late_end] if x is not None]
        return min(l) if l else None


    @late_end.setter
    def late_end(self, value):
        self.prop_late_end = value


class Artefact(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=1024, null=True, blank=True)
    task = models.ForeignKey("TaskLeaf", null=False, on_delete=models.CASCADE, related_name="artefact")

    def __str__(self):
        return self.title + ' - ' + self.task.name


class TaskGroup(TaskComponent):
    pass


class StructureComponent(models.Model):
    parent = models.ForeignKey("Division", null=True, blank=True, on_delete=models.SET_NULL, related_name="child")


class Division(StructureComponent):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name


class Employee(StructureComponent):
    full_name = models.CharField(max_length=255, null=False)
    short_name = models.CharField(max_length=255, null=True, blank=True)
    position = models.ForeignKey("Position", null=True, blank=True, on_delete=models.SET_NULL)
    login = models.CharField(max_length=32, null=True, unique=True, blank=True)
    salt = models.CharField(max_length=32, null=True, blank=True)
    hash = models.CharField(max_length=32, null=True, blank=True)
    isadmin = models.BooleanField(null=False, default=False)

    def __str__(self):
        return (self.short_name if self.short_name else self.full_name) + (', ' + self.position.name if self.position else '')


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
