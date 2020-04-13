from django.contrib import admin

from .models import Student, Price, District, Lesson, Money, Level

admin.site.register(Student)
admin.site.register(Price)
admin.site.register(Lesson)
admin.site.register(District)
admin.site.register(Money)
admin.site.register(Level)

# Register your models here.
