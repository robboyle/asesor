from twilio import twiml
import logging

from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings

from forms import RegistrationForm
from models import PhoneNumber, Question

log = logging.getLogger('asesor')

# Registration Views #

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            
            if user:
                from django.contrib.auth import login
                login(request, user)
                                    
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = RegistrationForm()
        
    return render_to_response('register.html', {
                                'form' : form,
                              }, context_instance=RequestContext(request))


# Interface Views #
def about(request):
    return render_to_response('about.html', {}, context_instance=RequestContext(request))

@login_required
def dashboard(request):
    if request.user.get_profile().user_type == 'doctor':
        return dash_doctor(request)
    elif request.user.get_profile().user_type == 'translator':
        return dash_translator(request)

    raise Http404
    
def dash_translator(request):
    callback_qs = request.user.translating_questions.filter(is_answered=True, is_calledback=False).order_by('timestamp')
    translate_qs = request.user.translating_questions.filter(is_translated=False).order_by('timestamp')
    available_qs = Question.objects.filter(
                                        translator=None, is_translated=False
                                    ).filter(
                                        language__in=request.user.get_profile().languages.all()
                                    ).order_by('timestamp')
 
    return render_to_response('dash_translator.html', {
                                    'callback_qs': callback_qs,
                                    'translate_qs': translate_qs,
                                    'available_qs': available_qs
                                }, context_instance=RequestContext(request))

def dash_doctor(request):
    answer_qs = request.user.doctor_questions.filter(is_answered=False).order_by('timestamp')
    available_qs = Question.objects.filter(
                                        doctor=None, is_translated=True
                                    ).order_by('timestamp')

    return render_to_response('dash_doctor.html', {
                                    'answer_qs': answer_qs,
                                    'available_qs': available_qs
                                }, context_instance=RequestContext(request))


@login_required
def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.user.get_profile().user_type == 'doctor':
        return question_doctor(request, question)
    elif request.user.get_profile().user_type == 'translator':
        return question_translator(request, question)
        
    raise Http404
    
def question_translator(request, question):
    if question.translator and not question.translator == request.user:
        return HttpResponseRedirect(reverse('dashboard'))
    
    if request.method == "POST":
        if 'set_translator' in request.POST:
            question.translator = request.user
        if 'translation' in request.POST:
            question.translation = request.POST['translation']
        if 'is_translated' in request.POST:
            question.is_translated = request.POST['is_translated']
        if 'is_calledback' in request.POST:
            question.is_calledback = request.POST['is_calledback']
         
        question.save()   
            
        if ('is_calledback' in request.POST and question.is_calledback) or ('is_translated' in request.POST and question.is_translated):
            return HttpResponseRedirect(reverse('dashboard'))
    
    if question.is_translated:
        from twilio.util import TwilioCapability
        
        capability = TwilioCapability(settings.TWILIO_ACCT_SID, settings.TWILIO_AUTH_TOKEN)
        capability.allow_client_outgoing(settings.TWILIO_OUTGOING_APP_ID)        
        capability_token = capability.generate()
    else:
        capability_token = ''
            
    return render_to_response('question_translator.html', {
                                        'question': question,
                                        'capability_token': capability_token,
                                    }, context_instance=RequestContext(request))
    
def question_doctor(request, question):
    if question.doctor and not question.doctor == request.user:
        return HttpResponseRedirect(reverse('dashboard'))
    
    if request.method == "POST":
        if 'set_doctor' in request.POST:
            question.doctor = request.user
        if 'answer' in request.POST:
            question.answer = request.POST['answer']
        if 'is_answered' in request.POST:
            question.is_answered = request.POST['is_answered']
        
        question.save()
           
        if question.is_answered:
            return HttpResponseRedirect(reverse('dashboard'))                    
    
    return render_to_response('question_doctor.html', {
                                        'question': question
                                    }, context_instance=RequestContext(request))
     
# Twilio Views #

questions = {
    'en': {
        'intro': "Please state your question clearly and some one will get back to you."
    },
    'es': {
        'intro': "Por favor escriba su pregunta de forma clara y alguien se pondra en contacto contigo."
    },
    'de': {
        'intro': "Bitte geben Sie Ihre Frage klar und jemand werden uns umgehend bei Ihnen."
    },
}
@csrf_exempt                       
def call(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    to = request.POST['To']
    number = PhoneNumber.objects.get(number=to)
    language = number.language
    
    r = twiml.Response()
    r.say(questions[language.code]['intro'], language=language.code)
    r.record(playBeep=True, action='/create_question/')
    
    return HttpResponse(r)

@csrf_exempt    
def create_question(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST']) 
    
    recording_url = request.POST['RecordingUrl']
    recording_url.replace('2010-04-01', '2008-08-01')
    to_number = request.POST['To']
    from_number = request.POST['From']
    
    number = PhoneNumber.objects.get(number=to_number)
    language = number.language
    
    log.debug(recording_url)
    
    q = Question(to_number=to_number,
                 from_number=from_number,
                 language=language, 
                 recording_url=recording_url)
    q.save()

    log.debug('Question Created: %s' % q)

    r = twiml.Response()
    r.hangup()
    
    return HttpResponse(r)
    
@csrf_exempt
def call_patient(request):
    log.debug('Patient call received!')
    
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
        
    if 'question_id' not in request.POST:
        return Http404
        
    log.debug('Patient call for question: %s' % request.POST['question_id'])
        
    question = get_object_or_404(Question, pk=request.POST['question_id'])    
    
    r = twiml.Response()
    r.dial(number=question.from_number, callerId=settings.TWILIO_CALLER_ID)
    
    log.debug('Question Found! Dialing patient: %s' % question.from_number)
    log.debug(r)
    
    return HttpResponse(r)















