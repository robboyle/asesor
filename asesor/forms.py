from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from models import USER_TYPES, Language, UserProfile

class RegistrationForm(forms.ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
        help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
   
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    user_type = forms.ChoiceField(label=_("I am a"), widget=forms.RadioSelect, choices=USER_TYPES)

    languages = forms.MultipleChoiceField(label=_("I am able to translate the following to English"), required=False)

    class Meta:
        model = User
        fields = ("username", "user_type",)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['languages'].choices = [( l.id, l.name.capitalize()) for l in Language.objects.all()]
        
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
        
    def clean(self):
        user_type = self.cleaned_data.get("user_type")
        languages = self.cleaned_data.get("languages")
        
        if user_type == "translator" and not languages:
            self._errors["languages"] = self.error_class(["A translator must specify at least one fluent language."])
        
        return self.cleaned_data

    def save(self):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        
        profile = UserProfile()
        profile.user_type = self.cleaned_data["user_type"]
        profile.user = user
        profile.save()
        
        profile.languages = Language.objects.filter(pk__in=self.cleaned_data["languages"])
        profile.save()
            
        return user
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        