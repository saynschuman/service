from rest_framework.response import Response


# modified success response
def response_success(code, message, data, status):
    return Response({'status': 'success', 'code': code, 'message': message, 'data': data}, status=status)


# modified error response
def response_error(code, message, data, status):
    return Response({'status': 'error', 'code': code, 'message': message, 'data': data}, status=status)
