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
    default_lesson_time = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.second_name)+' '+str(self.first_name)

    def calculate_age(self):
        today = datetime.date.today()
        if self.birthday:
            full_year = (today.month, today.day) < (self.birthday.month, self.birthday.day)
            return today.year - self.birthday.year - full_year
        else:
            return 0

    def calculate_seniority(self):
        if self.start_date is None: return f'Неизвестная дата начала взаимодействия'
        today = datetime.date.today()
        full_year = (today.month, today.day) < (self.start_date.month, self.start_date.day)
        years = today.year - self.start_date.year - full_year
        if years > 1:
            return f'Более {years} лет'
        elif years > 0:
            return f'1 год и {(today - self.start_date).days} дней'
        else:
            return f'{(today - self.start_date).days} дней'

    def tarif_live(self):
         price = self.prices.filter(skype=False).order_by('-start_date')
         if price: return price[0].tariff()
         return 0

    def tarif_skype(self):
         price = self.prices.filter(skype=True).order_by('-start_date')
         if price: return price[0].tariff()
         return 0

    def balance(self):
        income = float(sum(payment.transaction for payment in self.payments.all()))
        debt = sum(lesson.cost() for lesson in self.lessons.filter(status=1))
        return income-debt


class Price(models.Model):
    cost = models.DecimalField(verbose_name='price for lesson', max_digits=10, decimal_places=2)
    duration = models.IntegerField(verbose_name='Default duration of lesson')
    start_date = models.DateField(default=datetime.date.today)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='prices')
    skype = models.BooleanField(default=False)

    def __str__(self):
        skype_text = 'Skype' if self.skype else 'Live'
        return f'{skype_text} {self.student} from {self.start_date} = {self.cost}'

    def tariff(self):
        return round(int(self.cost) / int(self.duration), 2)


class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lessons')
    date = models.DateTimeField(default=datetime.datetime.today)
    lesson_long = models.IntegerField()
    skype = models.BooleanField(default=False)
    status = models.IntegerField(default=0, choices=CHOICES_LESSON_STATUS)
    location = models.CharField(max_length=256, blank=True, null=True)
    googlecal_event_id = models.CharField(max_length=1024, blank=True, null=True)
    googlecal_updated = models.DateTimeField(blank=True, null=True)
    googlecal_status = models.CharField(max_length=32, blank=True, null=True)
    googlecal_summary = models.CharField(max_length=256, blank=True, null=True)
    googlecal_description = models.TextField(blank=True, null=True)


    def __str__(self):
        skype_text = 'Skype' if self.skype else 'Live'
        return f'[{self.status}] {skype_text} {self.date.date()}: {self.lesson_long}min with {self.student}'

    def delete(self):
        self.status = 4
        self.save()

    def cost(self):
        price = self.student.prices\
            .filter(start_date__lte=self.date, skype=self.skype)\
            .order_by('-start_date')\
            .first()
        if price:
            return round(price.tariff() * self.lesson_long, 2)
        return 0

    @property
    def gcal_format(self):
        skype_text = 'Skype: ' if self.skype else ''
        google_status = 'cancelled' if self.status == 4 else 'confirmed'
        data = {
            'summary': f'{self.student} - {self.cost()}',
            'location': f'{self.student.district}',
            'description': f'{skype_text}{self.get_status_display()}',
            'start_date': self.date,
            'end_date': self.date+datetime.timedelta(minutes=self.lesson_long),
            'status': google_status,
        }
        return data

class Money(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField(default=datetime.date.today)
    transaction = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.date}: {self.transaction} Rub from {self.student}'