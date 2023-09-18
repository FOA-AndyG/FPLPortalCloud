from urllib.parse import urlparse

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from Django_apps.HomeApp.functions.dashboard_function import process_get_dashboard_data, process_get_container_data, \
    process_inventory_remaining_data, get_time_range
from Django_apps.HomeApp.functions.login_function import user_authentication
from Django_apps.HomeApp.functions.session_function import *


def login(request):
    # clear session
    request.session.flush()
    print("login view")
    content = {
        "title": "FPLS Portal",
        "footer": "© Furniture Pros Logistics Solution 2022"
    }
    user_ip = get_client_ip(request)
    print("IP: ", user_ip)

    if request.method == "POST" and 'login_button' in request.POST:
        if user_authentication(request):
            # return redirect("HomeApp:new_home_page")
            return redirect("OMSOrderApp:web_scan_page")
        else:
            return redirect("/login")

    return render(request, "home/pages/login.html", content)


def logout(request):
    request.session.flush()
    return redirect("/login")


def home(request):
    print("home view")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    ip = get_client_ip(request)
    print(ip)
    reset_session_timestamp(request)
    user = get_session_user(request)
    print(user.fullname)

    content = {
        "user": user,
        "column_names": ["1", "2"]
    }
    return render(request, "home/pages/home.html", content)


# New layout test
def new_home_page(request):
    print("new_home_page")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    ip = get_client_ip(request)
    print(ip)
    user = get_session_user(request)
    print(user.fullname)
    select_dict = {
        "Daily": f"Daily {get_time_range('Daily')[0]}",
        "Weekly": f"Weekly {get_time_range('Weekly')[0]} - {get_time_range('Weekly')[1]}",
        "Monthly": f"Monthly {get_time_range('Monthly')[0]} - {get_time_range('Monthly')[1]}"
    }
    content = {
        "title": "Dashboard",
        "page_head": "Dashboard",
        "user": user,
        "select_dict": select_dict
    }
    content.update(process_get_dashboard_data("Weekly"))
    if request.method == "POST" and 'order_confirm_btn' in request.POST:
        date_type = request.POST.get("order_select")
        content.update(process_get_dashboard_data(date_type))

    return render(request, "new_home/pages/home.html", content)


def dashboard_order_ajax(request):
    print()


def dashboard_total_upcoming_container_ajax(request):
    print("dashboard_total_upcoming_container_ajax")
    response_data = {
        "result": False,
        "msg": "Invalid request",
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        try:
            response_data.update(process_get_container_data())
        except Exception as e:
            response_data["msg"] = str(e)

    return JsonResponse(response_data)


def dashboard_inventory_remaining_ajax(request):
    print("dashboard_inventory_remaining_ajax")
    response_data = {
        "result": False,
        "msg": "Invalid request",
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        try:
            response_data.update(process_inventory_remaining_data())
        except Exception as e:
            response_data["msg"] = str(e)

    return JsonResponse(response_data)

