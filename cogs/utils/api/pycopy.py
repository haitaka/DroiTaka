# coding: utf-8

import json

import requests

__version__ = '0.1.2-dev'
USER_AGENT = 'pycopy/{}'.format(__version__)
BASE_URL = 'https://api.copy.com'
AUTH_URL = BASE_URL + '/auth_user'  # TODO: should use /rest
OBJECTS_URL = BASE_URL + '/list_objects'  # TODO: should use /rest
DOWNLOAD_URL = BASE_URL + '/download_object'  # TODO: should use /rest

class Copy(object):

	def __init__(self, username, password):
		self.session = requests.session()
		self.session.headers.update({'X-Client-Type': 'api',
									 'X-Api-Version': '1',
									 'User-Agent': USER_AGENT, })
		self.authenticate(username, password)

	def _get(self, url, *args, **kwargs):
		return self.session.get(url, *args, **kwargs)

	def _post(self, url, data, *args, **kwargs):
		return self.session.post(url, {'data': json.dumps(data), }, *args,
								 **kwargs)

	def authenticate(self, username, password):
		response = self._post(AUTH_URL,
							  {'username': username, 'password': password, })
		json_response = response.json()
		if 'auth_token' not in json_response:
			raise ValueError("Error while authenticating")

		self.user_data = json_response
		self.auth_token = json_response['auth_token']
		self.session.headers.update({'X-Authorization': self.auth_token, })

	def list_files(self, dir_path):
		file_list = []
		list_wtrmark = False
		while (True):
			response = self._post(OBJECTS_URL, {'path': dir_path, 'list_watermark': list_wtrmark, })
			for file in response.json()['children']:
				if file['type'] == 'file':
					file_list.append(file['path'].split("/")[-1])
					#print(file_list[-1])
			list_wtrmark = response.json()['list_watermark']
			#print(list_wtrmark)
			#print(response.json())
			if (response.json()['more_items'] == '0'):
				#print('break')
				break
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
