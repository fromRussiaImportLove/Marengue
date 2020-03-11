from django.contrib import admin

from .models import Student, Price, District, Lesson

admin.site.register(Student)
admin.site.register(Price)
admin.site.register(Lesson)
admin.site.register(District)

# Register your models here.
