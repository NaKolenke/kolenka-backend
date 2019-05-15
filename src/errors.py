class ErrorResponse:
  code = 0
  message = ''

  def __init__(self, code, message):
    self.code = code
    self.message = message

# Error messages

error_not_found = ErrorResponse(1, 'Not found')
error_no_access = ErrorResponse(2, 'No access')
