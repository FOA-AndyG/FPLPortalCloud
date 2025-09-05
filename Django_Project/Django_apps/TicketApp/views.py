from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from django.contrib import messages
from django.utils import timezone

from Django_apps.HomeApp.functions.session_function import check_login_status, get_session_user_username, \
    get_session_user_location

# Create your views here.
from Django_apps.TicketApp.forms import LtlStorageForm
from Django_apps.TicketApp.models import *

PAGE_PATH = "TicketApp/pages/"


def landing_view(request):
    """
    Displays the initial choice page for the driver: Pickup or Drop Trailer.
    """
    if not check_login_status(request):
        return redirect("HomeApp:login")

    content = {
        "title": "Landing Page",
        "page_head": "Landing Page",
    }

    return render(request, PAGE_PATH + "landing_view.html", content)


# Using @login_required is the standard Django way to protect views.
# It automatically handles redirection to the login page.

def storage_create_view(request):
    if not check_login_status(request):
        return redirect("HomeApp:login")

    if request.method == "POST":
        form = LtlStorageForm(request.POST)
        if form.is_valid():
            try:
                # Use a transaction to ensure both record and log are created successfully
                with transaction.atomic():
                    # Create the record object but don't save to DB yet
                    record = form.save(commit=False)
                    record.operator = request.session.get("username", "anonymous")
                    record.status = "Pending"  # Or your desired default status
                    record.save()

                    # Now create the associated log entry
                    OperationLog.objects.create(
                        record=record,
                        action="created",
                        operator=request.session.get("username", "anonymous"),
                        note=f"Staged to bin location {record.location_code}",
                    )
                messages.success(request, f"Successfully staged Picking Slip # {record.picking_no}!")
                # Redirect to a fresh form after success (Post/Redirect/Get pattern)
                return redirect("TicketApp:storage_create")
            except Exception as e:
                # Catch any unexpected database errors
                messages.error(request, f"An error occurred: {e}")
    else:
        # For a GET request, create a new empty form instance
        form = LtlStorageForm()

    context = {'form': form}
    return render(request, PAGE_PATH+"storage_create.html", context)


def storage_search_view(request):
    if not check_login_status(request):
        return redirect("HomeApp:login")

    query = None
    results = None

    if request.method == "GET" and "scan" in request.GET:
        query = request.GET.get("scan_code", "").strip()
        if query:
            # Try BOL search first
            results = LtlStorageRecord.objects.filter(bol_no=query)
            if not results.exists():
                # If not found, try Location Code search
                results = LtlStorageRecord.objects.filter(location_code=query, status="Pending")

            if not results.exists():
                results = None
                messages.warning(request, f"No records found for '{query}'")

    return render(
        request,
        PAGE_PATH + "storage_search.html",
        {"query": query, "results": results}
    )


def storage_confirm_view(request, record_id):
    if not check_login_status(request):
        return redirect("HomeApp:login")

    record = get_object_or_404(LtlStorageRecord, id=record_id)

    if record.status == "Shipped":
        messages.warning(request, "This order has been shipped！")
        return redirect("TicketApp:storage_search")

    operator = request.session.get("username", "anonymous")

    record.status = "Shipped"
    record.sent_at = timezone.now()
    record.save()

    # 写日志
    OperationLog.objects.create(
        record=record,
        action="Shipped",
        operator=operator,
        note="picked up and shipped",
    )

    messages.success(request, f"BOL {record.bol_no} has been shipped！")
    return redirect("TicketApp:storage_search")


def storage_logs_view(request, record_id):
    record = get_object_or_404(LtlStorageRecord, id=record_id)
    logs = record.logs.all().order_by("-created_at")  # 按时间倒序
    return render(request, PAGE_PATH+"storage_logs.html", {"record": record, "logs": logs})
