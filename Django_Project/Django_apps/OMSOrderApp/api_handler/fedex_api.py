import json
import re

import requests


class FedExTrackingApp:
    def __init__(self, sandbox=True):
        # WYD FEDEX account - Test
        self.payload_token_test = {
            "grant_type": "client_credentials",
            "client_id": "l7d6506d7f92014907bd11ef5378582913",
            "client_secret": "be15ef9016314e93a4742f9b54a9d94c"
        }
        # WYD FEDEX account - Production
        self.payload_token = {
            "grant_type": "client_credentials",
            "client_id": "l7d950a2dc3d714d53aa053ff2cfc519b2",
            "client_secret": "4f7ef992089c47a1a53e048696519861"
        }

    def get_access_token(self):
        url = "https://apis.fedex.com/oauth/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.post(url, headers=headers, data=self.payload_token)
            if response.status_code == 200:
                token_response = response.json()
                access_token = token_response['access_token']
                return {"success": True, "msg": access_token}
            else:
                msg = f"Error obtaining access token: {response.status_code} - {response.text}"
                return {"success": False, "msg": msg}
        except Exception as err:
            return {"success": False, "msg": f"Error obtaining access token: {str(err)}"}

    def get_fedex_status(self, access_token, tracking_number):
        url = "https://apis.fedex.com/track/v1/trackingnumbers"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        data = {
            "trackingInfo": [
                {
                    "trackingNumberInfo": {
                        "trackingNumber": tracking_number
                    }
                }
            ],
            "includeDetailedScans": True
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            print(f"Checking: {tracking_number}")
            if response.status_code == 200:
                tracking_response = response.json()

                # Writing tracking_response to sample.json
                # with open('sample.json', 'w') as f:
                #     json.dump(tracking_response, f, indent=4)

                if tracking_response.get('output', {}).get('completeTrackResults'):
                    tracking_status = tracking_response['output']['completeTrackResults'][0]['trackResults'][0]['latestStatusDetail']['description']
                    return tracking_status
                else:
                    return "No tracking information"
            else:
                return f"{response.status_code} - {response.text}"
        except Exception as err:
            return f"Error obtaining tracking status: {str(err)}"


def is_valid_fedex_tracking_number(tracking_number):
    if re.match(r'^[27]\d{11}$', tracking_number):  # 12-digit starting with 2 or 7
        return True
    return False


def download_view(request):
    if request.method == "POST" and 'import_button' in request.POST:
        data = {'跟踪号': ['123456789012', '234567890123', '789012345678']}
        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response[
            'Content-Disposition'] = f"attachment; filename=tracking_status_result.xlsx"
        df.to_excel(response, index=False)
        return response

    return render(request, PAGE_PATH + "fedex_tracking_status_checking.html")