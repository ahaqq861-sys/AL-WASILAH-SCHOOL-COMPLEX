from django.db import models


class SchoolBranding(models.Model):
    school_name = models.CharField(
        max_length=255, default="Al-Wasilah School Complex"
    )
    tagline = models.CharField(
        max_length=255, default="Knowledge and Virtue", blank=True, null=True
    )
    primary_color = models.CharField(max_length=7, default="#800020")
    secondary_color = models.CharField(
        max_length=7, default="#1A252C"
    )  # <--- Ensure this field is present

    def __str__(self):
        return self.school_name