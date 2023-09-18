from datetime import datetime

from Django_apps.HomeApp.models import Login


def check_login_status(request):
    if "userid" in request.session.keys():
        return True
    else:
        return False


def check_is_department_limited(request):
    if request.session['department'] in request.session['limited_department']:
        return True
    else:
        return False


# TODO: request.session['_session_init_timestamp_'] will auto refresh on every request.
# TODO: request.session['timestamp'] is control by developer for the future use.
def reset_session_timestamp(request):
    # request.session['_session_init_timestamp_']

    # current_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    # request.session['timestamp'] = current_time
    current_time = datetime.now()
    temp_time = datetime.timestamp(current_time)
    request.session['timestamp'] = temp_time


# def set_session_status_online(request):
#     request.session['status'] = "online"
#
#
# def set_session_status_offline(request):
#     request.session['status'] = "offline"


# def get_session_status(request):
#     return request.session['status']


def set_session_user_id(request, user_id):
    request.session['userid'] = user_id


def get_session_user_id(request):
    return request.session['userid']


def set_session_user_username(request, user_username):
    request.session['username'] = user_username


def get_session_user_username(request):
    return request.session['username']


def get_session_user_fullname(request):
    user = Login.objects.get(id=get_session_user_id(request))
    return user.fullname


def get_session_user(request):
    user = Login.objects.get(id=get_session_user_id(request))
    return user


def set_session_user_location(request, location):
    request.session['location'] = location


def get_session_user_location(request):
    return request.session['location']


def set_session_user_department(request, department):
    request.session['department'] = department


def get_session_user_department(request):
    return request.session['department']


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def set_session_limited_department(request):
    request.session["limited_department"] = ["Cennos", "Test"]


def set_access_level(request, department):
    access_level = {
        "Everything": 99,
        "IT": 1,
        "Accounting": 2,
        "Customer Service": 3,
        "Operations": 4,
        "Purchase": 5,
        "FOAJL": 6,
        "Scanner": 7,
        "Picker": 8,
    }
    try:
        request.session["access_level"] = access_level.get(department)
    except Exception as e:
        request.session["access_level"] = 0

