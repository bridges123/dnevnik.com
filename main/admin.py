from django.contrib import admin
from .models import StudentProfile, TeacherProfile, Mark, Subject, School, Class, WorkingPlan


admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(Mark)
admin.site.register(Subject)
admin.site.register(Class)
admin.site.register(School)
admin.site.register(WorkingPlan)

