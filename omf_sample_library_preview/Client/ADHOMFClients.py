from __future__ import annotations

from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType
from ..Models.OMFData import OMFData
from .Authentication import Authentication
from ..Services import DataService

import gzip
import json
import logging

from .OMFClient import OMFClient

import requests


class ADHOMFClients(object):
    """Handles communication with ADH OMF Endpoint."""

    def __init__(
        self):
        self.__adhOMFClients: list[OMFClient] = []
        

    @property
    def Clients(self) -> list[OMFClient]:
        """
        Gets the base url
        :return:
        """
        return self.__adhOMFClients

    def addClient(
        self,
        client: OMFClient,
    ) -> requests.Response:
        """
        """
        self.__adhOMFClients.append(client)
    
    
    def updateData(
        self,
        omf_data: list[OMFData],
    ) -> requests.Response:
        """
        Base OMF request function
        :param message_type: OMF message type
        :param action: OMF action
        :param omf_data: OMF data
        :return: Http response
        """

        
        omf_message_json = [obj.toDictionary() for obj in omf_data]
        body = json.dumps(omf_message_json)
        logging.debug(f"omf body: {body}")
        compressed_body = gzip.compress(bytes(body, 'utf-8'))

        for client in self.__adhOMFClients:
            data_service = DataService(client)
            data_service.updateDataBody(compressed_body)
    
