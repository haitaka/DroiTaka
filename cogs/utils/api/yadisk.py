# coding: utf-8

import json
import requests

DEVICE_ID = '141f72b7-fd02-11e5-981a-00155d860f42'
DEVICE_NAME = 'DroiTaka'
CLIENT_ID = 'b12710fc26ee46ba82e34b97f08f2305'
CLIENT_SECRET = '4ff2284115644e04acc77c54526364d2'

class YaDisk(object):

	def __init__(self, token):
		self.session = requests.session()
		self.session.headers.update({'Authorization': 'OAuth ' + str(token),})
		
	def get_key_url():
		format_url = "https://oauth.yandex.ru/authorize?response_type=code&client_id={}&device_id={}&device_name={}&force_confirm=yes"
		return format_url.format(CLIENT_ID, DEVICE_ID, DEVICE_NAME)
		
	def get_token(key):
		res = requests.post('https://oauth.yandex.ru/token', data = {
			'grant_type': 'authorization_code',
			'code': key,
			'client_id': CLIENT_ID,
			'client_secret': CLIENT_SECRET,
			'device_id': DEVICE_ID,
			'device_name': DEVICE_NAME,
		})
		print(res.text)
		return res.json()['access_token']

	def _get(self, url, *args, **kwargs):
		return self.session.get(url, *args, **kwargs)

	def _post(self, url, data, *args, **kwargs):
		return self.session.post(url, {'data': json.dumps(data), }, *args, **kwargs)
		
	def _put(self, url, *args, **kwargs):
		return self.session.put(url, *args, **kwargs)


	def list_files(self, dir_path):
		file_list = []
		res = self._get("https://cloud-api.yandex.net:443/v1/disk/resources", 
		                params={"path": "app:/" + dir_path,
		                        "limit": "0",})
		res = self._get("https://cloud-api.yandex.net:443/v1/disk/resources", 
		                params={"path": "app:/" + dir_path,
		                        "limit": res.json()['_embedded']['total']})
		for file in res.json()['_embedded']['items']:
			if file['type'] == 'file':
				file_list.append(file['name'])
		return file_list

	def direct_link(self, file_path):
		response = self._get("https://cloud-api.yandex.net:443/v1/disk/resources/download", 
		                     params={"path": "app:/" + file_path,})
		return response.json()['href']

	def upload(self, file_path, file):
		response = self._get("https://cloud-api.yandex.net:443/v1/disk/resources/upload", 
		                     params={"path": "app:/" + file_path,
		                             "overwrite": "true",})
		try:
			upload_url = response['href']
			self._put(upload_url, data = file)
		except:
			print('upload error')
		
