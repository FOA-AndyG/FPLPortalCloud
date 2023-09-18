
from django.contrib import messages

from Django_apps.HomeApp.functions.session_function import *
from Django_apps.HomeApp.models import *


def user_authentication(request):
    username = request.POST.get('username')
    user_input_password = request.POST.get('password')
    if username is not None and user_input_password is not None:
        user = get_user_from_database(username)
        if user is not None:
            if is_password_correct(user.password, user_input_password):
                request.session.set_expiry(60 * 60 * 3)  # 3 hours

                set_session_user_id(request, user.id)
                set_session_user_username(request, user.username)
                set_session_user_location(request, user.location)
                set_session_user_department(request, user.department)
                set_session_limited_department(request)
                set_access_level(request, user.department)
                reset_session_timestamp(request)
                # todo record user login activity
                # ipaddress = get_client_ip(request)
                # print(username, ipaddress)
                # insert_login_record(username, ipaddress)
                return True
            else:
                messages.error(request, "Password is not correct.")
                # return "WrongPassword"
        else:
            messages.error(request, "User does not exist.")
            # return "UserDoseNotExist"  # User does not exist
    else:
        messages.error(request, "Invalid input.")
        # return "InvalidInput"  # User does not exist


def get_user_from_database(username):
    try:
        user = Login.objects.exclude(location='EC').get(username=username)
        return user
    except Exception as e:
        return None


def is_password_correct(user_password, user_input):
    if user_password == user_input:
        return True
    else:
        return False


# def insert_login_record(username, ipaddress):
#     record = BranchLoginRecord(username=username, ipaddress=ipaddress)
#     record.save()
