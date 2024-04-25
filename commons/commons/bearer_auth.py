from requests import Request, auth


class BearerAuth(auth.AuthBase):
    """
    Custom bearer authentication for requests library.
    """

    def __init__(self, token: str) -> None:
        """
        Initializes BearerAuth object attributes.

        :param token: Bearer token to be added to Authorization header.
        """
        self._token = token

    def __call__(self, request: Request) -> Request:
        """
        Adds Bearer token to request object.

        :param request: Request to be modified.

        :return: Request object with Authorization bearer added.
        """
        request.headers['Authorization'] = f'Bearer {self._token}'
        return request
