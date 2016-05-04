# coding: utf-8

import json
import requests

class VkAudio(object):

	def __init__(self, token):
		self.session = requests.session()
		self.session.params = {'access_token': token, }

	def _get(self, url, *args, **kwargs):
		return self.session.get(url, *args, **kwargs)
		
	def get_by_url(self, url):
		name = url.split("/")[-1]
		user_res = self._get("https://api.vk.com/method/user.get", 
		                     params={"user_ids": name, "fields": "id",}).json()
		if 'error' not in user_res:
			return self.get_user_audio(user_res['response'][0]['id'])
		group_res = self._get("https://api.vk.com/method/groups.getById", 
		                     params={"group_ids": name, "fields": "id",}).json()
		if 'error' not in group_res:
			return self.get_group_audio(group_res['response'][0]['id'])
		return []

	def get_user_audio(self, user_id):
		response = self._get("https://api.vk.com/method/audio.get", 
		                     params={"owner_id": user_id,
		                             "need_user": 0,})
		result = []
		try:
			data = response.json()['response']['items']
		except:
			return result
		for song in data:
			result.append({'artist': song['artist'],
			               'title': song['title'],
			               'url',: song['url'],})
		return result

	def get_group_audio(self, user_id):
		response = self._get("https://api.vk.com/method/audio.get", 
		                     params={"owner_id": "-" + str(user_id),
		                             "need_user": 0,})
		result = []
		try:
			data = response.json()['response']['items']
		except:
			return result
		for song in data:
			result.append({'artist': song['artist'],
			               'title': song['title'],
			               'url',: song['url'],})
		return result
		
