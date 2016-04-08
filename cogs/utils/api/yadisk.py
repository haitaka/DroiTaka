import json
import requests

class YaDisk(object):

	def __init__(self, token):
		self.session = requests.session()
		self.session.headers.update({'Authentication': 'OAuth ' + str(token),})
		
	def get_token(key):
		res = self._post('http://oauth.yandex.ru/token', data = {
			'grant_type': 'authorization_code',
			'code': key,
			'client_id': 'b12710fc26ee46ba82e34b97f08f2305',
			'client_secret': '4ff2284115644e04acc77c54526364d2',
			'device_id': '141f72b7-fd02-11e5-981a-00155d860f42',
			'device_name': 'DroiTaka',
		})
		return res.json()['access_token']

	def _get(self, url, *args, **kwargs):
		return self.session.get(url, *args, **kwargs)

	def _post(self, url, data, *args, **kwargs):
		return self.session.post(url, {'data': json.dumps(data), }, *args, **kwargs)

	def list_files(self, dir_path):
		file_list = []
		res = self._get("https://cloud-api.yandex.net:443/v1/disk/resources", params={"path": dir_path,})
		for file in res.json()['_embedded']['items']:
			if file['type'] == 'file':
				file_list.append(file['name'])
		return file_list

	def direct_link(self, file_path):
		response = self.session._get("https://cloud-api.yandex.net:443/v1/disk/resources/download", 
		                             params={"path": file_path,})
		return response.json()['href']
