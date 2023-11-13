import json

import requests
from bs4 import BeautifulSoup


class LensCrawler:
    SCRIPT_SELECTOR = '#__NEXT_DATA__'

    def __init__(self, log_function=print):
        self.log_function = log_function
        self.json = {}

    def log(self, str):
        if self.log_function:
            self.log_function(str)

    def get_lens(self, url):
        try:
            body = self._load_url(url)
            if body is None:
                return None

            soup = BeautifulSoup(body, 'html.parser')
            script_content = soup.select_one(self.SCRIPT_SELECTOR).text
            json_data = json.loads(script_content)

            if json_data and json_data.get('props', {}).get('pageProps', {}).get('lensDisplayInfo'):
                return self._lens_info_to_lens(json_data['props']['pageProps']['lensDisplayInfo'])
        except Exception as e:
            self.log(e)
        return None

    def _load_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.log(e)
        return None

    def _lens_info_to_lens(self, lens_info):
        uuid = lens_info.get('scannableUuid', '')
        return {
            'unlockable_id': lens_info.get('lensId', ''), 'uuid': uuid,
            'snapcode_url': f'https://app.snapchat.com/web/deeplink/snapcode?data={uuid}&version=1&type=png',
            'user_display_name': lens_info.get('lensCreatorDisplayName', ''),
            'lens_name': lens_info.get('lensName', ''), 'lens_tags': '', 'lens_status': 'Live',
            'deeplink': lens_info.get('unlockUrl', ''), 'icon_url': lens_info.get('iconUrl', ''),
            'thumbnail_media_url': lens_info.get('lensPreviewImageUrl', ''),
            'thumbnail_media_poster_url': lens_info.get('lensPreviewImageUrl', ''),
            'standard_media_url': lens_info.get('lensPreviewVideoUrl', ''), 'standard_media_poster_url': '',
            'obfuscated_user_slug': '', 'image_sequence': {}, 'lens_id': lens_info.get('lensId', ''),
            'lens_url': lens_info.get('lensResource', {}).get('archiveLink', ''),
            'signature': lens_info.get('lensResource', {}).get('signature', ''), 'hint_id': '',
            'additional_hint_ids': {}
        }
