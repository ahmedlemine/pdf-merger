from rest_framework.exceptions import APIException


class MergeException(APIException):
    status_code = 500
    default_detail = "Something went wrong while trying to merge the PDF files."
    default_code = "internal_server_error"
