from __future__ import annotations

import json
import logging

from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType
from .Authentication import Authentication
from .OMFClient import OMFClient


class ADHOMFClient(OMFClient):
    """Handles communication with ADH OMF Endpoint."""

    def __init__(
        self,
        resource: str,
        api_version: str,
        account_id: str,
        omfingress_id: str,
        client_id: str = None,
        client_secret: str = None,
        omf_version: str = '1.2',
        logging_enabled: bool = False,
    ):
        self.__resource = resource
        self.__api_version = api_version
        self.__account_id = account_id
        self.__omfingress_id = omfingress_id
        self.__full_path = f'https://{resource}/api/account/{account_id}/omfingress/{omfingress_id}/v1/omf'

        if client_id is not None:
            self.__auth_object = Authentication(
                account_id, resource, client_id, client_secret
            )
            self.__auth_object.getToken()
        else:
            self.__auth_object = None

        super().__init__(self.FullPath, omf_version, True, logging_enabled)

    @staticmethod
    def fromAppsettings(path: str = None):
        if not path:
            path = 'appsettings.json'

        try:
            with open(
                path,
                'r',
            ) as f:
                appsettings = json.load(f)
        except Exception as error:
            logging.ERROR(f'Error: {str(error)}')
            logging.ERROR(f'Could not open/read appsettings.json')
            exit()

        return ADHOMFClient(
            appsettings.get('Resource'),
            appsettings.get('ApiVersion'),
            appsettings.get('AccountId'),
            appsettings.get('OmfIngressId'),
            appsettings.get('ClientId'),
            appsettings.get('ClientSecret'),
            appsettings.get('LoggingEnabled', False),
        )

    @property
    def Resource(self) -> str:
        """
        Gets the base url
        :return:
        """
        return self.__resource

    @property
    def ApiVersion(self) -> str:
        """
        Returns just the base api versioning information
        :return:
        """
        return self.__api_version

    @property
    def AccountId(self) -> str:
        """
        Returns the account ID
        :return:
        """
        return self.__account_id

    @property
    def OmfIngress(self) -> str:
        """
        Returns the Omfingress ID
        :return:
        """
        return self.__omfingress_id

    @property
    def FullPath(self) -> bool:
        return self.__full_path

    def _getToken(self) -> str:
        """
        Gets the bearer token
        :return:
        """
        return self.__auth_object.getToken()

    def getHeaders(self, message_type: OMFMessageType, action: OMFMessageAction):
        headers = super().getHeaders(message_type, action)
        headers['Request-Timeout'] = str(600)
        headers['authorization'] = f'Bearer {self._getToken()}'
        return headers
