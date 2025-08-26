from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import csv
import json
from .models import Poll, Option, Vote
from .forms import PollForm, OptionForm, LoginForm,SignUpForm


# --------------------------------------------------------------------------------------------------------------
# -----------------------------------User registration----------------------------------------------------------
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('poll_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# --------------------------------------------------------------------------------------------------------------
# -----------------------------------User Login-------------------------------------------------------------
def user_login(request):
    if request.user.is_authenticated:
        return redirect('poll_list')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                # Redirect to next page if specified
                next_page = request.POST.get('next') or request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('poll_list')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


# --------------------------------------------------------------------------------------------------------------
# -----------------------------------Logout-------------------------------------------------------------
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('poll_list')


# --------------------------------------------------------------------------------------------------------------
# List all polls 
# ------------------------------------------------------------------------------------------------------------
def poll_list(request):
    polls = Poll.objects.filter(is_active=True).order_by('-created_at')
    user_votes = {}
    
    if request.user.is_authenticated:
        # Get polls where user has already voted
        voted_polls = Vote.objects.filter(user=request.user).values_list('poll', flat=True)
        user_votes = {poll_id: True for poll_id in voted_polls}
    
    return render(request, 'poll_list.html', {
        'polls': polls,
        'user_votes': user_votes
    })


# --------------------------------------------------------------------------------------------------------------
# show all user voted poles (only authenticated user)
# --------------------------------------------------------------------------------------------------------------
@login_required
def my_votes(request):
    user_votes = Vote.objects.filter(user=request.user).select_related('poll', 'option').order_by('-voted_at')
    return render(request, 'my_votes.html', {'user_votes': user_votes})


# --------------------------------------------------------------------------------------------------------------
# show poll details (only authenticated user)
# --------------------------------------------------------------------------------------------------------------
@login_required
def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, is_active=True)
    
    # Check if poll is expired
    if poll.is_expired():
        messages.warning(request, 'This poll has expired and is no longer accepting votes.')
        return redirect('poll_results', poll_id=poll.id)
    
    # Check if user has already voted
    has_voted = Vote.objects.filter(user=request.user, poll=poll).exists()
    
    if request.method == 'POST' and not has_voted:
        option_id = request.POST.get('option')
        if option_id:
            try:
                option = get_object_or_404(Option, id=option_id, poll=poll)
                Vote.objects.create(user=request.user, poll=poll, option=option)
                messages.success(request, 'Your vote has been recorded!')
                return redirect('poll_results', poll_id=poll.id)
            except IntegrityError:
                messages.error(request, 'You have already voted on this poll!')
    
    return render(request, 'poll_detail.html', {
        'poll': poll,
        'has_voted': has_voted
    })


# --------------------------------------------------------------------------------------------------------------
# show poll resut 
# --------------------------------------------------------------------------------------------------------------
def poll_results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    user_vote = None
    
    if request.user.is_authenticated:
        try:
            user_vote = Vote.objects.get(user=request.user, poll=poll)
        except Vote.DoesNotExist:
            pass
    
    return render(request, 'results.html', {
        'poll': poll,
        'user_vote': user_vote
    })


# --------------------------------------------------------------------------------------------------------------
# Show poll result
# --------------------------------------------------------------------------------------------------------------
def poll_results_json(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    data = {
        'question': poll.question,
        'total_votes': poll.total_votes(),
        'options': []
    }
    
    for option in poll.options.all():
        data['options'].append({
            'text': option.text,
            'votes': option.vote_count(),
            'percentage': option.vote_percentage()
        })
    
    return JsonResponse(data)


# --------------------------------------------------------------------------------------------------------------
# Export to csv formate
# --------------------------------------------------------------------------------------------------------------
def export_poll_results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="poll_{poll.id}_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Poll Question', poll.question])
    writer.writerow(['Created By', poll.created_by.username])
    writer.writerow(['Created At', poll.created_at.strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Total Votes', poll.total_votes()])
    writer.writerow([])
    writer.writerow(['Option', 'Votes', 'Percentage'])
    
    for option in poll.options.all():
        writer.writerow([option.text, option.vote_count(), f"{option.vote_percentage():.1f}%"])
    
    writer.writerow([])
    writer.writerow(['Detailed Vote Records'])
    writer.writerow(['Username', 'Option', 'Vote Date'])
    
    votes = Vote.objects.filter(poll=poll).select_related('user', 'option').order_by('-voted_at')
    for vote in votes:
        writer.writerow([vote.user.username, vote.option.text, vote.voted_at.strftime('%Y-%m-%d %H:%M:%S')])
    
    return response


# --------------------------------------------------------------------------------------------------------------
# Create poll (only admin can create)
# --------------------------------------------------------------------------------------------------------------
@login_required
def create_poll(request):
    # Check if user is admin/staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to create polls.')
        return redirect('poll_list')
    
    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        
        # Get the options from POST data
        options_data = []
        for key in request.POST:
            if key.startswith('option_'):
                option_text = request.POST[key].strip()
                if option_text:
                    options_data.append(option_text)
        
        if poll_form.is_valid() and len(options_data) >= 2:
            poll = poll_form.save(commit=False)
            poll.created_by = request.user
            poll.save()
            
            # Create options
            for option_text in options_data:
                Option.objects.create(poll=poll, text=option_text)
            
            messages.success(request, f'Poll "{poll.question}" created successfully!')
            return redirect('poll_list')
        else:
            if len(options_data) < 2:
                messages.error(request, 'Please provide at least 2 options.')
    else:
        poll_form = PollForm()
    
    return render(request, 'create_poll.html', {
        'poll_form': poll_form
    })



# --------------------------------------------------------------------------------------------------------------
# Admin can manage polls (activate and deactivate)
# --------------------------------------------------------------------------------------------------------------
@login_required
def manage_polls(request):
    # Check if user is admin/staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to manage polls.')
        return redirect('poll_list')
    
    polls = Poll.objects.all().order_by('-created_at')
    return render(request, 'manage_polls.html', {'polls': polls})

@login_required
def toggle_poll_status(request, poll_id):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to manage polls.')
        return redirect('poll_list')
    
    poll = get_object_or_404(Poll, id=poll_id)
    poll.is_active = not poll.is_active
    poll.save()
    
    status = "activated" if poll.is_active else "deactivated"
    messages.success(request, f'Poll "{poll.question}" has been {status}.')
    return redirect('manage_polls')
