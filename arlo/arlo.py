"""
A package for interacting with Netgear's Arlo camera system via their API.
"""
##
# Copyright 2016 Jeffrey D. Walter
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
import functools
import logging

import requests


log = logging.getLogger(__name__)


def check_login(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._user_id is None:
            log.error('User called %s without logging in first', func.__name__)
            raise Exception('You must login before calling this method')
        return func(self, *args, **kwargs)
    return wrapper


class Arlo(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.headers = {}
        self._user_id = None
        self.base_url = 'https://arlo.netgear.com/hmsweb/'

    def _get_body(self, request):
        """
        Takes a request, checks for HTTP errors, then returns the request's JSON

        Args:
            request: A requests.Request object

        Returns:
            JSON
        """
        request.raise_for_status()
        return request.json()

    def _get(self, url, headers={}):
        """
        Calls requests.get() on the specified URL with the specified headers

        Args:
            url: string URL
            headers: dictionary to be used as headers in the request

        Returns:
            JSON
        """
        headers.update(self.headers)
        r = requests.get(url, headers=headers)
        return self._get_body(r)

    def _post(self, url, body, headers={}):
        """
        Calls requests.post() on the specified URL with the specified headers

        Args:
            url: string URL
            body: dictionary of data to send in the request
            headers: dictionary to be used as headers in the request

        Returns:
            JSON
        """
        headers.update(self.headers)
        r = requests.post(url, json=body, headers=headers)
        return self._get_body(r)

    def _put(self, url, body, headers={}):
        """
        Calls requests.put() on the specified URL with the specified headers

        Args:
            url: string URL
            body: dictionary of data to send in the request
            headers: dictionary to be used as headers in the request

        Returns:
            JSON
        """
        headers.update(self.headers)
        r = requests.put(url, json=body, headers=headers)
        return self._get_body(r)
    
    def login(self): 
        """
        Logs a user into the Arlo service. Sets the authorization token header and user ID
        if the request was successful.

        Args: 

        Returns:
            HTTP 400 on bad login or JSON
            {
              "userId": "XXX-XXXXXXX",
              "email": "user@example.com",
              "token": "some token",
              "paymentId": "XXXXXXXX",
              "authenticated": 1472961381,
              "accountStatus": "registered",
              "serialNumber": "XXXXXXXXXXXXX",
              "countryCode": "US",
              "tocUpdate": false,
              "policyUpdate": false,
              "validEmail": true
            }
        """
        body = self._post(self.base_url+'login', {'email': self.username, 'password': self.password})
        if body['success']:
            self.headers = {
                'Authorization': body['data']['token']
            }
            self._user_id = body['data']['userId']
        return body

    @check_login
    def logout(self):
        """
        Logs a user out of the Arlo service
        
        Args: 

        Returns:  JSON
        """
        ret = self._put(self.base_url+'logout', {})
        if ret['success']:
            self._user_id = None
            self.headers = {}
        return ret

    # Configure The Schedule (Calendar) - {"from": "XXX-XXXXXXX_web","to": "XXXXXXXXXXXXX","action": "set","resource": "schedule","transId": "web!XXXXXXXX.XXXXXXXXXXXXXXXXXXXX","publishResponse": true,"properties": {"schedule": [{"modeId": "mode0","startTime": 0},{"modeId": "mode2","startTime": 28800000},{"modeId": "mode0","startTime": 64800000},{"modeId": "mode0","startTime": 86400000},{"modeId": "mode2","startTime": 115200000},{"modeId": "mode0","startTime": 151200000},{"modeId": "mode0","startTime": 172800000},{"modeId": "mode2","startTime": 201600000},{"modeId": "mode0","startTime": 237600000},{"modeId": "mode0","startTime": 259200000},{"modeId": "mode2","startTime": 288000000},{"modeId": "mode0","startTime": 324000000},{"modeId": "mode0","startTime": 345600000},{"modeId": "mode2","startTime": 374400000},{"modeId": "mode0","startTime": 410400000},{"modeId": "mode0","startTime": 432000000},{"modeId": "mode0","startTime": 518400000}]}
    # Create Mode -
    #    {"from": "XXX-XXXXXXX_web","to": "XXXXXXXXXXXXX","action": "add","resource": "rules","transId": "web!XXXXXXXX.XXXXXXXXXXXXXXXXXXXX","publishResponse": true,"properties": {"name": "Record video on Camera 1 if Camera 1 detects motion","id": "ruleNew","triggers": [{"type": "pirMotionActive","deviceId": "XXXXXXXXXXXXX","sensitivity": 80}],"actions": [{"deviceId": "XXXXXXXXXXXXX","type": "recordVideo","stopCondition": {"type": "timeout","timeout": 15}},{"type": "sendEmailAlert","recipients": ["__OWNER_EMAIL__"]},{"type": "pushNotification"}]}}
    # Delete Mode - {"from": "XXX-XXXXXXX_web","to": "XXXXXXXXXXXXX","action": "delete","resource": "modes/mode3","transId": "web!XXXXXXXX.XXXXXXXXXXXXXXXXXXXX","publishResponse": true}
    # Camera Off - {"from": "XXX-XXXXXXX_web","to": "XXXXXXXXXXXXX","action": "set","resource": "cameras/XXXXXXXXXXXXX","transId": "web!XXXXXXXX.XXXXXXXXXXXXXXXXXXXX","publishResponse": true,"properties": {"privacyActive": false}}
    # Night Vision On - {"from": "XXX-XXXXXXX_web","to": "XXXXXXXXXXXXX","action": "set","resource": "cameras/XXXXXXXXXXXXX","transId": "web!XXXXXXXX.XXXXXXXXXXXXXXXXXXXX","publishResponse": true,"properties": {"zoom": {"topleftx": 0,"toplefty": 0,"bottomrightx": 1280,"bottomrighty": 720},"mirror": true,"flip": true,"nightVisionMode": 1,"powerSaveMode": 2}}
    # Motion Detection Test - {"from": "XXX-XXXXXXX_web","to": "XXXXXXXXXXXXX","action": "set","resource": "cameras/XXXXXXXXXXXXX","transId": "web!XXXXXXXX.XXXXXXXXXXXXXXXXXXXX","publishResponse": true,"properties": {"motionSetupModeEnabled": true,"motionSetupModeSensitivity": 80}}
    #
    # device_id = locations.data.uniqueIds
    #
    # System Properties:  ("resource": "modes")
    #   active (string) - Mode Selection (mode2 = All Motion On, mode1 = Armed, mode0 = Disarmed, etc.)
    #
    # System Properties:  ("resource": "schedule")
    #   active (bool) - Mode Selection (true = Calendar)
    #
    # Camera Properties:  ("resource": "cameras/{id}")
    #   privacyActive (bool) - Camera On/Off
    #   zoom (topleftx (int), toplefty (int), bottomrightx (int), bottomrighty (int)) - Camera Zoom Level
    #   mirror (bool) - Mirror Image (left-to-right or right-to-left)
    #   flip (bool) - Flip Image Vertically
    #   nightVisionMode (int) - Night Mode Enabled/Disabled (1, 0)
    #   powerSaveMode (int) - PowerSaver Mode (3 = Best Video, 2 = Optimized, 1 = Best Battery Life) 
    #   motionSetupModeEnabled (bool) - Motion Detection Setup Enabled/Disabled 
    #   motionSetupModeSensitivity (int 0-100) - Motion Detection Sensitivity
    ##
    def _notify(self, device_id, xcloud_id, body):
        """
        Posts to base URL for arming, disarming, changing modes, etc on the cameras.

        Args:
            device_id: The ID of the device being targeted, obtained from get_devices()
            xcloud_id: The xcloud_id obtained from get_devices(). Seems to be the same across all devices
            body: dictionary containing parameters for the specified operation

        Returns:
            JSON
        """
        return self._post(self.base_url+'users/devices/notify/'+device_id, body, headers={"xCloudId": xcloud_id})

    @check_login
    def get_modes(self, device_id, xcloud_id):
        """
        Get all modes for the specified device

        Args:
            device_id: The ID of the device being targeted, obtained from get_devices()
            xcloud_id: The xcloud_id obtained from get_devices(). Seems to be the same across all devices

        Returns:
            JSON
        """
        return
        # print('get modes')
        # print(self._notify(device_id, xcloud_id, {"from": self._user_id+"_web",
        #                                           "to": device_id,
        #                                           "action": "get",
        #                                           "resource": "modes",
        #                                           "publishResponse": "false"
        #                                           }))
        # print('get schedule')
        # print(self._notify(device_id, xcloud_id, {"from": self._user_id+"_web",
        #                                           "to": device_id,
        #                                           "action": "get",
        #                                           "resource": "schedule",
        #                                           "publishResponse": "false"
        #                                           }))
        # print('subscribing')
        # print(self._get(self.base_url+'client/subscribe?token='+self.headers['Authorization']))
        # print('set subscription')
        # print(self._notify(device_id, xcloud_id, {"from": self._user_id+"_web",
        #                                           "to": device_id,
        #                                           "action": "set",
        #                                           "resource": "subscription/"+self._user_id+"_web",
        #                                           "publishResponse": "false",
        #                                           "properties": {"devices": [device_id]}
        #                                           }))

    @check_login
    def arm(self, device_id, xcloud_id):
        """
        Arm the specified device

        Args:
            device_id: The ID of the device being targeted, obtained from get_devices()
            xcloud_id: The xcloud_id obtained from get_devices(). Seems to be the same across all devices

        Returns:
            JSON
        """
        return self._notify(device_id, xcloud_id, {"from": self._user_id+"_web",
                                                  "to": device_id,
                                                  "action": "set",
                                                  "resource": "modes",
                                                  "publishResponse": "true",
                                                  "properties": {"active": "mode1"}
                                                  })

    @check_login
    def disarm(self, device_id, xcloud_id):
        """
        Disarm the specified device

        Args:
            device_id: The ID of the device being targeted, obtained from get_devices()
            xcloud_id: The xcloud_id obtained from get_devices(). Seems to be the same across all devices

        Returns:
            JSON
        """
        return self._notify(device_id, xcloud_id, {"from": self._user_id+"_web",
                                                  "to": device_id,
                                                  "action": "set",
                                                  "resource": "modes",
                                                  "publishResponse": "true",
                                                  "properties": {"active": "mode0"}
                                                  })

    @check_login
    def custom_mode(self, device_id, xcloud_id, mode):
        """
        Enable the specified custom mode

        Args:
            device_id: The ID of the device being targeted, obtained from get_devices()
            xcloud_id: The xcloud_id obtained from get_devices(). Seems to be the same across all devices
            mode: string representing the custom mode name

        Returns:
            JSON
        """
        return self._notify(device_id, xcloud_id, {"from": self._user_id+"_web",
                                                   "to": device_id,
                                                   "action": "set",
                                                   "resource": "modes",
                                                   "publishResponse": "true",
                                                   "properties": {"active": mode}
                                                   })

    @check_login
    def delete_mode(self, device_id, xcloud_id, mode):
        """
        Delete the specified custom mode

        Args:
            device_id: The ID of the device being targeted, obtained from get_devices()
            xcloud_id: The xcloud_id obtained from get_devices(). Seems to be the same across all devices
            mode: string representing the custom mode name

        Returns:
            JSON
        """
        return self._notify(device_id, xcloud_id, {"from": self._user_id+"_web",
                                                   "to": device_id,
                                                   "action": "delete",
                                                   "resource": "modes/"+mode,
                                                   "publishResponse": "true"
                                                   })

    @check_login
    def toggle_camera(self, device_id, xcloud_id, active=True):
        """
        Toggle the camera between <WHAT>

        Args:
            device_id: The ID of the device being targeted, obtained from get_devices()
            xcloud_id: The xcloud_id obtained from get_devices(). Seems to be the same across all devices
            active:

        Returns:
            JSON
        """
        return self._notify(device_id, xcloud_id, {"from": self._user_id+"_web",
                                                   "to": device_id,
                                                   "action": "set",
                                                   "resource": "cameras/"+device_id,
                                                   "publishResponse": "true",
                                                   "properties": {"privacyActive": active}
                                                   })

    @check_login
    def reset(self):
    # TODO what is this?
    # when you delete a bunch of videos this gets called
        """
        Reset <WHAT>

        Args:

        Returns:
            JSON
        """
        return self._get(self.base_url+'users/library/reset')

    @check_login
    def get_service_level(self):
        """
        Get the user's current service plan level

        Args:

        Returns:
            JSON
        """
        return self._get(self.base_url+'users/serviceLevel')

    @check_login
    def get_payment_offers(self):
        """
        Get any available payment offers

        Args:

        Returns:
            JSON
        """
        return self._get(self.base_url+'users/payment/offers')

    @check_login
    def get_profile(self):
        """
        Retrieve the user's profile

        Args:

        Returns:
            JSON
        """
        return self._get(self.base_url+'users/profile')

    @check_login
    def get_friends(self):
        """
        Retrieve the user's friends

        Args:

        Returns:
            JSON
        """
        return self._get(self.base_url+'users/friends')

    @check_login
    def get_locations(self):
        """
        Retrieve the user's locations

        Args:

        Returns:
            JSON
        """
        return self._get(self.base_url+'users/locations')

    @check_login
    def get_devices(self):
        """
        Gets a list of all devices owned by the user and returns their metadata

        Args:

        Returns:
            JSON
        """
        return self._get(self.base_url+'users/devices')

    @check_login
    def get_library_metadata(self, from_date, to_date):
        """
        Retrieve metadata from the user's library between the specified dates

        Args:
            from_date: string following the format %Y%m%d, as in 20160907
            to_date: string following the format %Y%m%d, as in 20160907

        Returns:
            JSON
        """
        return self._post(self.base_url+'users/library/metadata', {'dateFrom': from_date, 'dateTo': to_date})
    
    @check_login
    def get_library(self, from_date, to_date):
        """
        Retrieves all videos in the library between the specified dates. Note that the presignedContentUrl
        is a link to the actual video, and the presignedThumbnailUrl is a link the thumbnail

        Args:
            from_date: string following the format %Y%m%d, as in 20160907
            to_date: string following the format %Y%m%d, as in 20160907

        Returns:
            JSON
        """
        return self._post(self.base_url+'users/library', {'dateFrom': from_date, 'dateTo': to_date})

    @check_login
    def update_profile(self, first_name, last_name):
        """
        Update the user's name on his/her profile

        Args:
            first_name: string
            last_name: string

        Returns:
            JSON
        """
        return self._put(self.base_url+'users/profile', {'firstName':  first_name, 'lastName':  last_name})

    @check_login
    def update_password(self, password):
        """
        Update the user's password 

        Args:
            password: string representing the user's new password

        Returns:
            JSON
        """
        body = self._post(self.base_url+'users/changePassword', {'currentPassword': self.password,'newPassword': password})
        self.password = password
        return body

    
    @check_login
    def update_friends(self, body):
        """
        Update the user's friends who have access to his/her cameras

        Args:
            body: A dictionary of the following format - 
                {
                  "firstName": "Some",
                  "lastName": "Body",
                  "devices": {
                    "XXXXXXXXXXXXX": "Camera 1",
                    "XXXXXXXXXXXXX": "Camera 2",
                    "XXXXXXXXXXXXX": "Camera 3"
                  },
                  "lastModified": 1463977440911,
                  "adminUser": true,
                  "email": "user@example.com",
                  "id": "XXX-XXXXXXX"
                }

        Returns:
            JSON
        """
        return self._put(self.base_url+'users/friends', body) 

    @check_login
    def update_device_name(self, parent_id, device_id, name):
        """
        Update the name of the specified device

        Args:
            parent_id: The parentId of the device, as specified in the device info from get_devices()
            device_id: The ID of the device being targeted, obtained from get_devices()
            name: string representing the new device name

        Returns:
            JSON
        """
        return self._put(self.base_url+'users/devices/renameDevice', {'deviceId': device_id, 'deviceName': name, 'parentId': parent_id})

    @check_login
    def update_display_order(self, body):
        """
        Update the order in which cameras are displayed to the user in the web and mobile interfaces

        Args:
            body: A dictionary of the form {"devices": {"device_id1": 1, "device_id2": 2, ...}}

        Returns:
            JSON
        """
        return self._post(self.base_url+'users/devices/displayOrder', body)

    @check_login
    def delete_recordings(self, recordings):
        """
        Delete recording(s) from the library

        Args:
            recordings: A list containing dictionaries of the form
            {"createdDate": "20160904","utcCreatedDate": 1473010280395,"deviceId": "XXXXXXXXXXXXX"}

        Returns:
            JSON
        """
        return self._post(self.base_url+'users/library/recycle', {'data': recordings})

    @check_login
    def get_recording(self, url, filename):
        """
        Download the specified video based on its presignedContentUrl and save it to disk

        Args:
            url: The video's presignedContentUrl
            filename: The file to save the video to

        Returns:
            None
        """
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(): 
                fd.write(chunk)

    @check_login
    def stream_recording(self, device_id):
        """
        A generator for streaming data from the specified camera

        Args:
            device_id: The ID of the device being targeted, obtained from get_devices()

        Returns:
            Byte data representing the video being streamed
        """
        body = self._post(self.base_url+'users/devices/startStream', {"from": self._user_id+"_web",
                                                                      "to": device_id,
                                                                      "action": "set",
                                                                      "resource": "cameras/"+device_id,
                                                                      "publishResponse": "true",
                                                                      "properties": {"activityState": "startPositionStream"}
                                                                        #  "transId": "web!XXXXXXXX.XXXXXXXXXXXXXXXXXXXX",
                                                                      })
        r = requests.get(body['data']['url'], stream=True)
        r.raise_for_status()
        for chunk in r.iter_content():
            yield chunk 

