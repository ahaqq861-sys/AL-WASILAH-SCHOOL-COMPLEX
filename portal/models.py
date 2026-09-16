from django.db import models


class SchoolBranding(models.Model):
    school_name = models.CharField(
        max_length=255, default="Al-Wasilah School Complex"
    )
    tagline = models.CharField(
        max_length=255, blank=True, default="Knowledge and Virtue"
    )
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#800020")

    def __str__(self):
        return self.school_name