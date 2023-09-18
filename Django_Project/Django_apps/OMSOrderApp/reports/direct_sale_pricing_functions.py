import os
from datetime import datetime

import pandas as pd
from django.core.files.storage import default_storage
from django.http import HttpResponse

from Django_apps.HomeApp.functions.session_function import get_session_user_username
from Django_apps.OMSOrderApp.models import FplDirectSalePricingLog


def get_price_log_display_data():
    display_data = FplDirectSalePricingLog.objects.all().order_by("-updated_date")[:100]
    return display_data


def search_price_log_data(request):
    search_sku = request.POST.get("search_text")
    if search_sku:
        display_data = FplDirectSalePricingLog.objects.filter(sku=search_sku).order_by("-updated_date")[:100]
    else:
        display_data = FplDirectSalePricingLog.objects.all().order_by("-updated_date")[:500]
    return display_data


def export_current_price_log_table(request, display_data):
    try:
        print('export_current_price_log_table')
        df = pd.DataFrame.from_records(
            display_data.values_list('sku', 'price', 'updated_date', 'username'),
            columns=['SKU', 'Direct Sale Price', 'Last Modify Date', 'Username']
        )

        file_save_path = f"static/OMSOrderApp/report_files/direct_sale_report/{get_session_user_username(request)}/export/"
        if not os.path.exists(file_save_path):
            os.makedirs(file_save_path, 777)
        current_time = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        result_file_name = f"Price_log_{current_time}.xlsx"
        df.to_excel(file_save_path + result_file_name, index=False)

        excel = open(file_save_path + result_file_name, "rb")
        response = HttpResponse(excel,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={result_file_name}'
        return {'result': True, 'response': response}
    except Exception as e:
        return {'result': False, 'msg': str(e)}
