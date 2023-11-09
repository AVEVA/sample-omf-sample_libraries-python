import requests

from ..Client.OMFClient import OMFClient
from ..Models.OMFType import OMFType
from ..Models.OMFMessageAction import OMFMessageAction
from ..Models.OMFMessageType import OMFMessageType


class TypeService:
    def __init__(self, omf_client: OMFClient):
        self.__omf_client = omf_client

    @property
    def OMFClient(self) -> OMFClient:
        return self.__omf_client

    def createTypes(self, omf_type: list[OMFType]):
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Type,
            OMFMessageAction.Create,
            omf_type)
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to create types')

    def updateTypes(self, omf_type: list[OMFType]):
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Type,
            OMFMessageAction.Update,
            omf_type)
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to update types')

    def deleteTypes(self, omf_type: list[OMFType]):
        response = self.__omf_client.retryWithBackoff(
            self.__omf_client.omfRequest,
            OMFMessageType.Type,
            OMFMessageAction.Delete,
            omf_type)
        self.__omf_client.verifySuccessfulResponse(response, 'Failed to delete types')
