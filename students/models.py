from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
import datetime

CHOICES_GENDER = [(1, 'man'), (0, 'woman')]
CHOICES_LESSON_STATUS = [(0, 'Planned'), (1, 'OK'), (2, 'Cancel client'), (3, 'Cancel Teacher'),
                         (4, 'Removed'), (7, 'Error')]


class District(models.Model):
    district_name = models.CharField(max_length=128)

    def __str__(self):
        return self.district_name


class Level(models.Model):
    level_name = models.CharField(max_length=30)
    rank = models.IntegerField(unique=True)

    def __str__(self):
        return self.level_name


class Source(models.Model):
    source_name = models.CharField(max_length=128)

    def __str__(self):
        return self.source_name


class Student(models.Model):
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    birthday = models.DateField(blank=True, null=True)
    gender = models.IntegerField(choices=CHOICES_GENDER)
    district = models.ForeignKey(District, on_delete=models.PROTECT, blank=True, null=True)
    level = models.ForeignKey(Level, on_delete=models.PROTECT, blank=True, null=True)
    active = models.BooleanField(default=True)
    phone = PhoneNumberField(blank=True, null=True, help_text='Contact phone number')
    email = models.EmailField(blank=True, null=True, unique=True)
    start_date = models.DateField(blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return str(self.second_name)+' '+str(self.first_name)


class Price(models.Model):
    cost = models.DecimalField(verbose_name='price for lesson', max_digits=10, decimal_places=2)
    duration = models.IntegerField(verbose_name='Default duration of lesson')
    start_date = models.DateField(default=datetime.date.today)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    skype = models.BooleanField(default=False)

    def __str__(self):
        return str(self.student) + ' from ' + str(self.start_date) + ' = ' + str(self.cost)

    def tariff(self):
        return round(int(self.cost) / int(self.duration) * 60, 2)


class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lessons')
    date = models.DateTimeField(default=datetime.datetime.today)
    lesson_long = models.IntegerField()
    skype = models.BooleanField(default=False)
    googlecal_event_id = models.CharField(max_length=1024, blank=True, null=True)
    status = models.IntegerField(default=0, choices=CHOICES_LESSON_STATUS)


    def __str__(self):
        return str(self.date) + ': ' + str(self.lesson_long) + 'min with ' + str(self.student)


class Money(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='balance')
    date = models.DateField(default=datetime.date.today)
    transaction = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.date) + ': ' + str(self.transaction) + 'Rub from' + str(self.student)