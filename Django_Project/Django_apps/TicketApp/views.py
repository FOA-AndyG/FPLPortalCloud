from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Ticket, Comment
from .forms import TicketForm, CommentForm
from datetime import datetime

from Django_apps.HomeApp.functions.session_function import check_login_status, get_session_user_username, \
    get_session_user_location

# Create your views here.
PAGE_PATH = "TicketApp/pages/"


def ticket_dashboard(request):
    print("ticket_dashboard page")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    content = {
        "title": "Ticket Dashboard",
        "page_head": "Ticket Dashboard",
        "df_title": "Ticket Dashboard Table",
        "display_columns": ['TicketID', 'Title', 'Description', 'Submitter', 'Assignee', 'CreateDate', 'UpdateDate'],
    }


    return render(request, PAGE_PATH + "ticket_dashboard.html", content)


def ticket_list(request):
    if not check_login_status(request):
        return redirect("HomeApp:login")

    username = get_session_user_username(request)
    location = get_session_user_location(request)

    tickets = Ticket.objects.filter(submitter=username).order_by('-created_at')
    return render(request, PAGE_PATH + 'ticket_list.html', {'tickets': tickets, 'username': username, 'location': location})


def ticket_detail(request, ticket_id):
    if not check_login_status(request):
        return redirect("HomeApp:login")

    username = get_session_user_username(request)
    location = get_session_user_location(request)

    ticket = Ticket.objects.get(ticket_id=ticket_id)
    comments = Comment.objects.filter(ticket_id=ticket_id).order_by('created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket_id = ticket_id
            comment.commenter = username
            comment.created_at = datetime.now()
            comment.save()
            return redirect('ticket_detail', ticket_id=ticket_id)
    else:
        form = CommentForm()

    return render(request, PAGE_PATH +'ticket_detail.html',
                  {'ticket': ticket, 'comments': comments, 'form': form, 'username': username, 'location': location})


def create_ticket(request):
    if not check_login_status(request):
        return redirect("HomeApp:login")

    username = get_session_user_username(request)
    location = get_session_user_location(request)

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.submitter = username
            ticket.created_at = datetime.now()
            ticket.status = 'Open'
            ticket.save()
            return redirect('ticket_list')
    else:
        form = TicketForm()

    return render(request, PAGE_PATH + 'create_ticket.html', {'form': form, 'username': username, 'location': location})


def assign_ticket(request, ticket_id):
    if not check_login_status(request):
        return redirect("HomeApp:login")

    username = get_session_user_username(request)
    location = get_session_user_location(request)

    if request.method == 'POST':
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        assignee = request.POST.get('assignee')
        ticket.assignee = assignee
        ticket.status = 'Assigned'
        ticket.save()
        return redirect('ticket_detail', ticket_id=ticket_id)


def api_get_tickets(request):
    if not check_login_status(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    username = get_session_user_username(request)
    location = get_session_user_location(request)

    tickets = Ticket.objects.filter(submitter=username).values()
    return JsonResponse(list(tickets), safe=False)


def api_create_ticket(request):
    if not check_login_status(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    username = get_session_user_username(request)
    location = get_session_user_location(request)

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.submitter = username
            ticket.created_at = datetime.now()
            ticket.status = 'Open'
            ticket.save()
            return JsonResponse({'success': True, 'ticket_id': ticket.ticket_id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})