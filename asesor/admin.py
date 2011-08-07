from django.contrib import admin

from models import UserProfile, Language, PhoneNumber, Question

admin.site.register(UserProfile)
admin.site.register(Language)
admin.site.register(PhoneNumber)
admin.site.register(Question)