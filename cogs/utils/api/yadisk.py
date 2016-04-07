import json

import requests

__version__ = '0.1.2-dev'
USER_AGENT = 'pycopy/{}'.format(__version__)
BASE_URL = 'https://api.copy.com'
AUTH_URL = BASE_URL + '/auth_user'  # TODO: should use /rest
OBJECTS_URL = BASE_URL + '/list_objects'  # TODO: should use /rest
DOWNLOAD_URL = BASE_URL + '/download_object'  # TODO: should use /rest

class Copy(object):

	def __init__(self, token):
		self.session = requests.session()
		self.session.headers.update({'Authentication': 'OAuth ' + str(token),})
		
	def get_token(self, key):
		res = requests.post('http://oauth.yandex.ru/token', data = {
			'grant_type': 'authorization_code',
			'code': key,
			'client_id': 'b12710fc26ee46ba82e34b97f08f2305',
			'client_secret': '4ff2284115644e04acc77c54526364d2',
			'device_id': '141f72b7-fd02-11e5-981a-00155d860f42',
			'device_name': 'DroiTaka',
		})

	def _get(self, url, *args, **kwargs):
		return self.session.get(url, *args, **kwargs)

	def _post(self, url, data, *args, **kwargs):
		return self.session.post(url, {'data': json.dumps(data), }, *args, **kwargs)

	def list_files(self, dir_path):
		file_list = []
		json_res = self._https://cloud-api.yandex.net:443/v1/disk/resources?path=%2Fradio%2F
		return file_list

	def direct_link(self, file_path):
		object_url = BASE_URL + '/rest/meta/copy/' + file_path
		response = self.session.get(object_url)
		return response.json()['url']
	
	def get_file(self, file_path):
		url = self.direct_link(file_path)
		r = self._post(DOWNLOAD_URL, {'path': file_path}, stream=True)
		r.raw.decode_content = True
		return r.raw
		
	def dwnload_file(self, file_path):
		url = self.direct_link(file_path)
		local_filename = "tmp_uploads/" + url.split('/')[-1]
		r = self._get(url, stream=True)
		with open(local_filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
					#f.flush() #commented by recommendation from J.F.Sebastian
		return local_filename
	
	def get_headers_str(self):
		headers_str = ""
		for key, value in self.session.headers.items():
			headers_str += "{}: {}\r\n".format(key, value)
		return headers_str
