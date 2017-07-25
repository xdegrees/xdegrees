import copy

import requests
from tornado.web import RequestHandler


class VersionHandler(RequestHandler):  # pylint: disable=W0223
    """
    Return the version of the service. This is useful for debugging and simple monitoring.
    """
    def get(self, *args, **kwargs):
        """
        Get service version information.
        Returns:
            JSON containing version string
        Example:
            ```json
            {
                "version": "2.0.0"
            }
            ```
        """
        __version__ = '0.0.1'  # TODO get this from the parent module
        self.write({'version': __version__})


class SeparationsSearchHandler(RequestHandler):  # pylint: disable=W0223
    """
    Handle search requests for the links between two people.
    """
    def initialize(    # pylint: disable=W0221
            self,
            search_url: str,
            search_timeout_seconds: int):
        self.search_url = search_url
        self.search_timeout_seconds = search_timeout_seconds

    def get(self, *args, **kwargs):
        """
        Get link details from the whitepages API. The request.arguments are passed directly
        through to the whitepages API.
        Returns:
            JSON containing link details, or JSON containing errors if something bad happens
        Example:
            ```json
            {
              "results": [
                {
                  "is_historical": false,
                  "type": "person_location",
                  "connections": [
                    "Person Lastname",
                    "1234 1st Ave S, Seattle WA 90210"
                  ]
                },
                {
                  "is_historical": false,
                  "type": "location_person",
                  "connections": [
                    "1234 1st Ave S, Seattle WA 90210"
                    "Another Person"
                  ]
                }
              ]
            }
            ```
        """
        # TODO validation would be nice, but for now pass through all arguments
        params = copy.deepcopy(self.request.arguments)
        # TODO tie this to other factors, eg desired wait time or whether the user is paying
        params['max_links'] = 3

        # the timeout value will be applied to both the connect timeout and the read timeout
        request_kwargs = {'params': params, 'timeout': self.search_timeout_seconds}

        try:
            response = requests.get(self.search_url, **request_kwargs)

            # pass through errors from the upstream API
            if response.status_code == 200:
                self.set_status(response.status_code)
                # wrap array in 'results' because of a potential cross-site security vulnerability
                self.write({'results': response.json()})
            elif response.status_code in (400, 404, 422, 500):
                self.set_status(response.status_code)
                try:
                    # the upstream error response is a map already, so no need to wrap it
                    self.write(response.json())
                except ValueError:
                    # sometimes when something bad happens, the upstream returns no response body
                    pass
            else:
                # no details
                self.set_status(response.status_code)
        except (ConnectionError, requests.Timeout):
            # network problem (e.g. DNS failure, refused connection, etc.)
            # or request timed out
            self.set_status(500)


class MainHandler(RequestHandler):  # pylint: disable=W0223
    """
    Handle the root (empty) path.
    """
    def get(self):    # pylint: disable=W0221
        """ Render the index page. """
        self.render('index.html')
