import json
import requests
import time
from urllib.parse import parse_qs, urlparse

class PSNClient():
    _PS_GRAPH_API = "https://web.np.playstation.com/api/graphql/v1/op"
    _PS_OAUTH_API = "https://ca.account.sony.com/api/authz/v3/oauth"
    _BASIC_AUTH_HEADER = "Basic YWM4ZDE2MWEtZDk2Ni00NzI4LWIwZWEtZmZlYzIyZjY5ZWRjOkRFaXhFcVhYQ2RYZHdqMHY="

    def __init__(self, npsso, refresh_token=None):
        if npsso is None:
            raise ValueError("npsso cannot be None")

        self.npsso = npsso
        self.refresh_token = refresh_token
    
    def get_oauth_code(self):
        params = {
            'access_type' : 'offline',
            'app_context' : 'inapp_ios',
            'auth_ver' : 'v3',
            'cid' : '60351282-8C5F-4D5E-9033-E48FEA973E11',
            'client_id' : 'ac8d161a-d966-4728-b0ea-ffec22f69edc',
            'darkmode' : 'true',
            'device_base_font_size' : 10,
            'device_profile' : 'mobile',
            'duid' : '0000000d0004008088347AA0C79542D3B656EBB51CE3EBE1',
            'elements_visibility' : 'no_aclink',
            'no_captcha' : 'true',
            'redirect_uri' : 'com.playstation.PlayStationApp://redirect',
            'response_type' : 'code',
            'scope' : 'psn:mobile.v1 psn:clientapp',
            'service_entity' : 'urn:service-entity:psn',
            'service_logo' : 'ps',
            'smcid' : 'psapp:settings-entrance',
            'support_scheme' : 'sneiprls',
            'token_format' : 'jwt',
            'ui' : 'pr'
        }

        headers = {
            'cookie': f'npsso={self.npsso}'
        }

        query_string = "&".join([f"{k}={v}" for k,v in params.items()])

        response = requests.get(f"{self._PS_OAUTH_API}/authorize?{query_string}", headers=headers, allow_redirects=False)
        return parse_qs(urlparse(response.headers.get('Location')).query)['code']

    def get_refresh_token(self, oauth_code):
        data = {
            'smcid' : 'psapp%3Asettings-entrance',
            'access_type' : 'offline',
            'code' : oauth_code,
            'service_logo' : 'ps',
            'ui' : 'pr',
            'elements_visibility' : 'no_aclink',
            'redirect_uri' : 'com.playstation.PlayStationApp://redirect',
            'support_scheme' : 'sneiprls',
            'grant_type' : 'authorization_code',
            'darkmode' : 'true',
            'device_base_font_size' : 10,
            'device_profile' : 'mobile',
            'app_context' : 'inapp_ios',
            'token_format' : 'jwt'
        }

        headers = {
            'Authorization': self._BASIC_AUTH_HEADER,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(f"{self._PS_OAUTH_API}/token", data=data, headers=headers, allow_redirects=False)
        j = response.json()

        self.refresh_token = j['refresh_token']

        return {
            'refresh_token': j['refresh_token'],
            'refresh_token_expiration': time.time() + j['refresh_token_expires_in']
        }
    
    def get_access_token(self):
        data = {
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
            'scope': 'psn:clientapp psn:mobile.v1',
            'token_format': 'jwt'
        }

        auth_header = {
            'Authorization': self._BASIC_AUTH_HEADER
        }

        response = requests.post(f"{self._PS_OAUTH_API}/token", data=data, headers=auth_header)

        return response.json()['access_token']

    def get_purchased_games(self):
        variables = {
            "isActive": True,
            "platform": [ "ps4","ps5" ],
            "size": 50,
            "start": 0,
            "sortBy": "productName",
            "sortDirection": "asc",
            "subscriptionService": "NONE"
        }

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "2c045408b0a4d0264bb5a3edfed4efd49fb4749cf8d216be9043768adff905e2"
            }
        }

        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'authority': 'web.np.playstation.com',
            'authorization': f'Bearer {self.get_access_token()}',
            'content-type': 'application/json',
            'origin': 'https://library.playstation.com',
            'referer': 'https://library.playstation.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.18 Safari/537.36 Edg/93.0.961.11'
        }

        url = f'{self._PS_GRAPH_API}?operationName=getPurchasedGameList&variables={json.dumps(variables)}&extensions={json.dumps(extensions)}'
        response = requests.get(url, headers=headers)
        return json.loads(response.text)

    def get_recent_games(self):
        variables = {
            "limit": 50,
            "categories" : "ps4_game,ps5_native_game"
        }

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "e780a6d8b921ef0c59ec01ea5c5255671272ca0d819edb61320914cf7a78b3ae"
            }
        }

        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'authority': 'web.np.playstation.com',
            'authorization': f'Bearer {self.get_access_token()}',
            'content-type': 'application/json',
            'origin': 'https://library.playstation.com',
            'referer': 'https://library.playstation.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.18 Safari/537.36 Edg/93.0.961.11'
        }

        url = f'{self._PS_GRAPH_API}?operationName=getUserGameList&variables={json.dumps(variables)}&extensions={json.dumps(extensions)}'
        response = requests.get(url, headers=headers)
        return json.loads(response.text)