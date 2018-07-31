from rest_framework.exceptions import APIException


class ProfileDoesNotExist(APIException):
    """
    This class is for handling exception error 
    for a profile that does not exist
    """

    status_code = 400
    default_detail = 'The requested profile does not exist.'
