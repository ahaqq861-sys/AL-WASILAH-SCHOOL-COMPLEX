from django.contrib import admin
from .models import UserProfile, SchoolBranding, AcademicTerm, Grade, FeeRecord, ClassLevel, Course

admin.site.register(UserProfile)
admin.site.register(SchoolBranding)
admin.site.register(AcademicTerm)
admin.site.register(Grade)
admin.site.register(FeeRecord)
admin.site.register(ClassLevel)
admin.site.register(Course)