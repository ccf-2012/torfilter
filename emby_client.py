
import hashlib
import urllib
import requests


class EmbyClient:
    def __init__(self, serverUrl, username, password):
        self.serverUrl = serverUrl
        self.username = username
        self.password = password

    def authenticate(self):
        url = self.serverUrl + "/Users/AuthenticateByName?format=json"

        message_data = {}
        message_data["username"] = urllib.parse.quote(self.username)
        message_data["password"] = hashlib.sha1(self.password.encode('utf-8')).hexdigest()
        message_data["pw"] = urllib.parse.quote(self.password)

        headers = self.getHeaders()

        # print("Auth Url     : %s" % url)
        # print("Auth Msg     : %s" % message_data)
        # print("Auth Headers : %s" % headers)
        response = requests.post(url, data=message_data, headers=headers)
        # print(str(response.text))
        if response:
            return response.json()
        return ''

    def getHeaders(self, user_info=None):

        auth_string = "MediaBrowser Client=\"TorFilter\",Device=\"FilterApi\",DeviceId=\"10\",Version=\"1\""

        if user_info:
            auth_string += ",UserId=\"" + user_info["User"]["Id"] + "\""

        headers = {}

        if user_info:
            headers["X-MediaBrowser-Token"] = user_info["AccessToken"]

        headers["Accept-encoding"] = "gzip"
        headers["Accept-Charset"] = "UTF-8,*"

        headers["X-Emby-Authorization"] = auth_string

        return headers

    def getUrlData(self, url, user_info):
        if url.find("{server}") != -1:
            url = url.replace("{server}", self.serverUrl)

        if url.find("{userid}") != -1:
            if "User" in user_info and "Id" in user_info["User"]:
                user_id = user_info["User"]["Id"]
                url = url.replace("{userid}", user_id)
            else:
                return ""

        headers = self.getHeaders(user_info)

        response = requests.get(url, headers=headers)
        return response.json()

    def getMediaList(self):
        user_info = self.authenticate()
        if not user_info:
            print("Authenticate Failed.")
            return []

        url = ('{server}/emby/Users/{userid}/Items' +
               '?Recursive=true' +
               '&Fields=Path,PremiereDate,CommunityRating,ProviderIds' +
               '&IsMissing=False' +
               '&IncludeItemTypes=Movie,Series' +
               '&ImageTypeLimit=0')

        response_data = self.getUrlData(url, user_info)
        if not response_data:
            print("getUrlData Failed.")
            return []

        item_list = response_data["Items"]
        return item_list

