from django.contrib.auth.models import User
from django.contrib.auth.views import login
from app.models import Choice, Poll
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect,render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.views.generic import ListView, DetailView
from os import path
from django.core.urlresolvers import reverse_lazy
import json
from django.contrib.auth.models import Group
import qrcode
from .forms import QRForm
from django.db.models import Count
from operator import truediv
# class PollListView(ListView):
#     """Renders the home page, with a list of all polls."""
#     model = Poll

#     def get_context_data(self, **kwargs):
#         context = super(PollListView, self).get_context_data(**kwargs)
#         context['title'] = 'Polls'
#         context['year'] = datetime.now().year
#         return context

# class PollDetailView(DetailView):
#     """Renders the poll details page."""
#     model = Poll

#     def get_context_data(self, **kwargs):
#         context = super(PollDetailView, self).get_context_data(**kwargs)
#         context['title'] = 'Poll'
#         context['year'] = datetime.now().year
#         return context

# class PollResultsView(DetailView):
#     """Renders the results page."""
#     model = Poll

#     def get_context_data(self, **kwargs):
#         context = super(PollResultsView, self).get_context_data(**kwargs)
#         context['title'] = 'Results'
#         context['year'] = datetime.now().year
#         return context

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance = RequestContext(request,
        {
            'title': 'Contact',
            'message': 'Your contact page.',
            'year': datetime.now().year,
        })
    )

def about(request):
    """Renders the about page."""
    
    
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance = RequestContext(request,
        {
            'title': 'About',
            'message': 'Your application description page.',
            'year': datetime.now().year,
        
        })
    )

def vote(request, poll_id):
    """Handles voting. Validates input and updates the repository."""
    poll = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'app/details.html', {
            'title': 'Poll',
            'year': datetime.now().year,
            'poll': poll,
            'error_message': "Please make a selection.",
    })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('app:results', args=(poll.id,)))

@login_required
def seed(request):
    """Seeds the database with sample polls."""
    samples_path = path.join(path.dirname(__file__), 'samples.json')
    with open(samples_path, 'r') as samples_file:
        samples_polls = json.load(samples_file)

    for sample_poll in samples_polls:
        poll = Poll()
        poll.text = sample_poll['text']
        poll.pub_date = timezone.now()
        poll.save()

        for sample_choice in sample_poll['choices']:
            choice = Choice()
            choice.poll = poll
            choice.text = sample_choice
            choice.votes = 0
            choice.save()

    return HttpResponseRedirect(reverse('app:home'))
'''def custom_login(request,**kwargs):
    if request.user.is_authenticated():
        return redirect(reverse_lazy('contact'))
    else:
        return redirect(reverse_lazy('login'))'''

def index(request):
    if request.user.is_authenticated():
        #return render(request, 'app/student.html',{})
        return redirect(reverse_lazy('student'))
    else:
        return redirect(reverse_lazy('login'))
def student(request,**kwargs):
    assert isinstance(request, HttpRequest)

    if request.method == "POST":
        form = QRForm(request.POST)
        if form.is_valid():
            
            # qr == post
            
            qr = form.save(commit=False)

            print str(qr.created_at)+str(qr.courseid)
            img = qrcode.make(str(qr.created_at)+str(qr.courseid))
            img.save("app/static/app/media/"+".png")#folder path

            return render(request, 'app/display_qr_code.html')

    else:
        form = QRForm()
    x=[]
    z=[]
    y=[]
    w=[]
    user_group=request.user.groups.all()
    user=request.user
    for i in user_group:
        obj = Choice.objects.raw('SELECT * FROM app_choice WHERE qr_id in (SELECT id FROM app_poll WHERE courseid = %s) and studentid=%s',[i.id,user.id])
        y.append(len(list(obj)))
    
    for i in user_group:
        z.append(len(Poll.objects.filter(courseid=i.id)))
   
   
    w=map(lambda x_y: truediv(*x_y), filter(lambda x_y: x_y[1] != 0, zip(y, z)))
   
    #w = map(truediv, y, z)
   
    w = map(lambda x: x * 100, w)
    print w
    return render(
        request,
        'app/studentmain.html',
        context_instance = RequestContext(request,
        {
            'title': 'Student',
            'year': datetime.now().year,
            'group_name': Group.objects.all(),
            'user':User.objects.all(),
            'user_group':request.user.groups.all(),
            'x':x,
            'z':z,
            'y':y,
            'w':w,
            'form':form,
        })
        )
def students(request,group_id=1):
    assert isinstance(request, HttpRequest)
    qrid= Poll.objects.filter(courseid=group_id)
    user=request.user
    do=Choice.objects.raw('SELECT * FROM app_choice WHERE qr_id in (SELECT id FROM app_poll WHERE courseid = %s) and studentid=%s',[group_id,user.id])
    students=Group.objects.get(id=group_id)
    x=[]
    count=0
    for i in qrid:
        flag=0
        for j in do:
            if i.created_at == j.created_at:
                flag=1
                count+=1
                x.append('P')
        if not flag:
            x.append('A')
    cnt1 = len(qrid)
    ans = count/float(cnt1)*100
    ans1 = 100-ans
    return render(
        request,
        'app/student.html',
        context_instance = RequestContext(request,
        {
            'title': 'Student',
            'year': datetime.now().year,
            'students':Group.objects.get(id=group_id),
            'qrid':Poll.objects.filter(courseid=group_id),
            'user':User.objects.all(),
            'ans':Choice.objects.filter(is_present=1,studentid=user.id),
            'group_name': Group.objects.all(),
            'attendance': Choice.objects.all(),
            'user_group':request.user.groups.all(),
            'do':Choice.objects.raw('SELECT * FROM app_choice WHERE qr_id in (SELECT id FROM app_poll WHERE courseid = %s) and studentid=%s',[group_id,user.id]),
            'x':x,
            'cnt':ans,
            'ans1':ans1,
        })
        )
def prof(request,group_id=1):
    qrid= Poll.objects.filter(courseid=group_id)
    user=request.user

    assert isinstance(request, HttpRequest)
    a=[]
    students=User.objects.filter(groups__id=group_id)
    for i in students:
        if not i.is_staff:
            a.append(Choice.objects.raw('SELECT * FROM app_choice WHERE qr_id in (SELECT id FROM app_poll WHERE courseid = %s) and studentid=%s',[group_id,i.id]))
    
    q={}
    it=0
    for k in a:
        x=[]
        for i in qrid:
            flag=0
            for j in k:
                if i.created_at == j.created_at:
                    flag=1
                    x.append('P')
            if not flag:
                x.append('A')
        q[it] = x
        it = it+1   
    return render(
        request,
        'app/prof.html',
        context_instance = RequestContext(request,
        {
            'qrid':Poll.objects.filter(courseid=group_id),
            'title': 'Student',
            'year': datetime.now().year,
            'students':User.objects.filter(groups__id=group_id),
            'user':User.objects.all(),
            'group_name': Group.objects.all(),
            'user_group':request.user.groups.all(),
            'do':Choice.objects.raw('SELECT * FROM app_choice WHERE qr_id in (SELECT id FROM app_poll WHERE courseid = %s)',[group_id]),
            'a':a,
            'q':q,
        })
        )
'''def home(request):
    return render(request, "home.html", {'username':request.user.username})'''