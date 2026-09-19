from django.contrib import admin
from .models import (
    UserProfile, SchoolBranding, AcademicTerm, Grade, FeeRecord, 
    PaymentTransaction, ClassLevel, Course, Attendance, TimetableSchedule, Announcement
)

admin.site.register(UserProfile)
admin.site.register(SchoolBranding)
admin.site.register(AcademicTerm)
admin.site.register(Grade)
admin.site.register(FeeRecord)
admin.site.register(PaymentTransaction)
admin.site.register(ClassLevel)
admin.site.register(Course)
admin.site.register(Attendance)
admin.site.register(TimetableSchedule)
admin.site.register(Announcement)