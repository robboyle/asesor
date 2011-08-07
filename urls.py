from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ayuda.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='auth_login'),
    url(r'^register/$', 'asesor.views.register', name='auth_register'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    
    url(r'^call/$', 'asesor.views.call', name='twilio_call'),
    url(r'^create_question/$', 'asesor.views.create_question', name='twilio_create_question'),
    url(r'^call_patient/$', 'asesor.views.call_patient', name='twilio_call_patient'),
    
    url(r'^$', 'asesor.views.about', name='about'),
    
    url(r'^dashboard/$', 'asesor.views.dashboard', name='dashboard'),
    
    url(r'^question/(?P<question_id>\d+)/$', 'asesor.views.question', name='question'),
)
