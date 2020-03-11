from django.db import models
import datetime

CHOICES_GENDER = [('m', 'man'), ('w', 'woman')]


class District(models.Model):
    district_name = models.CharField(max_length=128)

    def __str__(self):
        return self.district_name


class Student(models.Model):
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=CHOICES_GENDER)
    district = models.ForeignKey(District, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return str(self.second_name)+' '+str(self.first_name)


class Price(models.Model):
    cost = models.DecimalField(verbose_name='price for lesson', max_digits=10, decimal_places=2)
    duration = models.IntegerField(verbose_name='Default duration of lesson')
    start_date = models.DateField(default=datetime.date.today)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.student) + ' from ' + str(self.start_date) + ' = ' + str(self.cost)

    def tariff(self):
        return round(int(self.cost) / int(self.duration) * 60, 2)


class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    lesson_long = models.IntegerField()

    def __str__(self):
        return str(self.date) + ': ' + str(self.lesson_long) + 'min with ' + str(self.student)


