import os
from django.contrib import messages

from django.shortcuts import render, redirect

# Create your views here.
from Django_apps.HomeApp.functions.session_function import check_login_status, get_session_user_username
from Django_apps.ScanApp.functions.scan_function import scan_info_import_process

PAGE_PATH = "ScanApp/pages/"


def index(request):
    print("scan_label_index")
    if not check_login_status(request):
        return redirect("HomeApp:login")
    content = {
        "title": "Scan Page",
    }
    return render(request, PAGE_PATH + "scan_label_index.html", content)


def trailer_page(request, trailer_number):
    print("trailer_page")
    if not check_login_status(request):
        return redirect("HomeApp:login")
    user_name = get_session_user_username(request)

    content = {
        "title": trailer_number,
        "trailer_number": trailer_number,
        "username": user_name
    }
    return render(request, PAGE_PATH + "trailer_page.html", content)


def scan_info_import(request):
    print("scan_info_import")
    if not check_login_status(request):
        return redirect("HomeApp:login")

    content = {
        "title": "Scan Info Import",
        "page_head": "Scan Info Import",
    }
    if request.method == "POST" and 'import_button' in request.POST:
        print("scan_info_import POST")
        import_result = scan_info_import_process(request)
        # content["messages"] = import_result["msg"]
        return redirect("ScanApp:scan_info_import")

    return render(request, PAGE_PATH + "scan_info_import.html", content)



