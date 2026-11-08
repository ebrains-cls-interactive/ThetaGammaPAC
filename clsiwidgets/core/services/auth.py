import os


def retrieve_token():
    """ returns HTTP headers containing OIDC bearer token """
    try:
        from clb_nb_utils import oauth as clb_oauth
        token = clb_oauth.get_token()
    except (ModuleNotFoundError, ConnectionError):
        token = os.environ.get('CLB_AUTH')
        if token is None:
            raise RuntimeError("No auth token available. Could not retrieve a lab token or a CLB_AUTH environment"
                                " variable.")

    return token