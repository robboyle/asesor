from django.contrib.auth.models import User
from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2)
    
    def __unicode__(self):
        return self.name


USER_TYPES = (
    ('translator', 'Translator'),
    ('doctor', 'Doctor'),
)
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPES)
    languages = models.ManyToManyField(Language, blank=True)
    
    def __unicode__(self):
        return unicode(self.user)

        
class PhoneNumber(models.Model):
    number = models.CharField(max_length=50, unique=True)
    language = models.ForeignKey(Language)
    
    def __unicode__(self):
        return self.number
        

class Question(models.Model):
    to_number = models.CharField(max_length=50)
    from_number = models.CharField(max_length=50)
    language = models.ForeignKey(Language)
    timestamp = models.DateTimeField(auto_now_add=True)
    recording_url = models.CharField(max_length=250)
    
    translation = models.TextField(blank=True)
    answer = models.TextField(blank=True)

    translator = models.ForeignKey(User, related_name='translating_questions', null=True, blank=True)
    doctor = models.ForeignKey(User, related_name='doctor_questions', null=True, blank=True)
    
    is_translated = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)
    is_calledback = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "%s - %s" % (self.language, self.timestamp)
        
        
        
        
        
        
        
        
        
        
        
        