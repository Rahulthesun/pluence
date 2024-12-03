from django.core.management.base import BaseCommand
from django.http import HttpResponse , JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from base.models import TiktokDashboard
from base.views import hash_token , unhash_token
from pluence.settings import TIKTOK_CLIENT_KEY , TIKTOK_CLIENT_SECRET

import requests , decimal

class Command(BaseCommand):
    help = "Run Periodic Task"

    def handle(self, *args, **kwargs):
        dashboards = TiktokDashboard.objects.filter()
        if dashboards.exists():
            for dashboard in dashboards:
                
                access_token = unhash_token(dashboard.access_token)
                refresh_token = unhash_token(dashboard.refresh_token)
                access_token_url = "https://open.tiktokapis.com/v2/oauth/token/"
                payload = {
                    'client_key': TIKTOK_CLIENT_KEY,
                    'client_secret': TIKTOK_CLIENT_SECRET,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                    }
                try:
                    response = requests.post(access_token_url , data=payload)
                    if response.status_code == 200:
                        print("Access Token Fetch Successfull")
                        refreshed_access_token = response.json().get("access_token")
                        refreshed_refresh_token = response.json().get("refresh_token")
                        if refreshed_access_token is None or refreshed_refresh_token is None:
                            print("API Critical Error : Access Token Not Found After Access Token Refresh !!")
                        else:
                            dashboard.access_token = hash_token(refreshed_access_token)
                            dashboard.refresh_token =  hash_token(refreshed_refresh_token)
                            dashboard.save()
                            print("Saved Refreshed Access Token ...")

                            user_data_url = "https://open.tiktokapis.com/v2/user/info/"
                            headers = {
                                'Authorization': f'Bearer {dashboard.access_token}'
                            }
                            params = {
                                'fields': 'avatar_url,open_id,union_id,display_name,bio_description,profile_deep_link,is_verified,username,follower_count,likes_count,video_count'  # Requesting specific fields
                            }

                            try:
                                user_data = requests.get(user_data_url, headers=headers, params=params)
                                # Check if the request was successful
                                user_data.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
                            except requests.exceptions.RequestException as e:
                                # Catch all requests-related exceptions
                                print(f"An error occurred: {e}")
                            else:
                                # Access the response JSON only if no exception occurred
                                try:
                                    user_data_json = user_data.json()
                                    
                                except ValueError as e:
                                    # Handle cases where response is not valid JSON
                                    print(f"Error parsing JSON: {e}")

                                else:
                                    print("User Json Data Fetched")
                                    user_info = user_data_json.get('data', {}).get('user', {})
                                    if not user_info:
                                        return JsonResponse({"error": "User info not found in response"}, status=400)
                                
                                    dashboard.avatar_url = user_info.get('avatar_url')
                                    dashboard.open_id = user_info.get('open_id')
                                    dashboard.display_name = user_info.get('display_name')
                                    dashboard.profile_deep_link = user_info.get('profile_deep_link')
                                    dashboard.is_verified = user_info.get('is_verified')
                                    dashboard.follower_count = user_info.get('follower_count')
                                    dashboard.likes_count = user_info.get('likes_count')
                                    dashboard.video_count = user_info.get('video_count')
                                    dashboard.save()
                                    if dashboard.follower_count > 0  and dashboard.video_count > 0:
                                        dashboard.engagement_rate = decimal.Decimal((dashboard.likes_count/(dashboard.video_count * dashboard.follower_count))*100)
                                    else:
                                        dashboard.engagement_rate = decimal.Decimal(0)    
                                    dashboard.save()
                                    print("Tiktok Data Updated ...")


                except ValueError:
                    return JsonResponse(response.json() , status= response.status_code)
                