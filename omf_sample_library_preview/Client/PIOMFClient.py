from __future__ import annotations

import requests
from requests.auth import HTTPBasicAuth

from .OMFClient import OMFClient
from .Authentication import Authentication

from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType


class PIOMFClient(OMFClient):
    """Handles communication with PI OMF Endpoint."""

    def __init__(self, resource: str, username: str, password: str, omf_version: str = '1.2', logging_enabled: bool = False):
        self.__resource = resource
        self.__basic = HTTPBasicAuth(username, password)

        super().__init__(resource, omf_version, True, logging_enabled)

    @property
    def Resource(self) -> str:
        """
        Gets the base url
        :return:
        """
        return self.__resource

    def getHeaders(self, message_type: OMFMessageType, action: OMFMessageAction):
        headers = super().getHeaders(message_type, action)
        headers['x-requested-with'] = 'xmlhttprequest'
        return headers

    def request(self, method: str, url: str, params=None, data=None, headers=None, additional_headers=None, **kwargs) -> requests.Response:
        return super().request(method, url, params, data, headers, additional_headers, auth=self.__basic, **kwargs)