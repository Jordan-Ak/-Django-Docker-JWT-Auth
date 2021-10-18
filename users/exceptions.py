from rest_framework.exceptions import APIException

class ValidationError(APIException):
    status_code = 400
    default_detail = 'Bad Request'
    default_code = 'Bad Request'