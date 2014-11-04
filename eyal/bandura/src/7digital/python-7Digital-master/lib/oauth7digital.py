import httplib
import logging
import os
import re
import sys

import api_settings
import oauth2 as oauth # https://github.com/simplegeo/python-oauth2

SERVER = 'api.7digital.com'
API_VERSION = '1.2'
REQUEST_TOKEN_URL = 'https://%s/%s/oauth/requesttoken' % (SERVER, API_VERSION)
ACCESS_TOKEN_URL = 'https://%s/%s/oauth/accesstoken' % (SERVER, API_VERSION)
AUTHORIZATION_URL = 'https://account.7digital.com/%s/oauth/authorise'
LOGGER_NAME = 'Oauth7Digital.logger'

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

if api_settings.log_dir and api_settings.log_name:
    log_fd = open(os.path.join(api_settings.log_dir, api_settings.log_name))
    logger.addHandler(logging.StreamHandler(log_fd))


def _consumer():
    return oauth.Consumer(api_settings.oauthkey, api_settings.secret)


def _token_from_response_content(content):
    key = re.search(
        "<oauth_token>(\w.+)</oauth_token>",
        content).groups()[0]
    secret = re.search(
        "<oauth_token_secret>(\w.+)</oauth_token_secret>",
        content).groups()[0]

    return oauth.Token(key, secret)


def request_2legged(url):
    client = oauth.Client(_consumer())
    response, content = client.request(
        url,
        headers = {"Content-Type":"application/x-www-form-urlencoded"},
        body="country=%s" % api_settings.country
    )
    return response, content


def request_token():
    logger.info('\nOAUTH STEP 1')

    response, content = request_2legged(REQUEST_TOKEN_URL)

    if response['status'] == '200':
        return _token_from_response_content(content)

    return response, content


def authorize_request_token(token):
    keyed_auth_url = AUTHORIZATION_URL % api_settings.oauthkey
    logger.info('\nOAUTH STEP 2')
    auth_url="%s?oauth_token=%s" % (keyed_auth_url, token.key)

    # auth url to go to
    logger.info('Authorization URL:\n%s' % auth_url)
    oauth_verifier = raw_input(
        'Please go to the above URL and authorize the app. \
        Hit return when you have been authorized: '
    )

    return True


def request_access_token(token):
    logger.info('\nOAUTH STEP 3')
    client = oauth.Client(_consumer(), token=token)
    response, content = client.request(
            ACCESS_TOKEN_URL,
            headers={"Content-Type":"application/x-www-form-urlencoded"}
    )

    return _token_from_response_content(content)


def request_3legged(url, access_token):
    ''' Once you have an access_token authorized by a customer,
        execute a request on their behalf
    '''
    client = oauth.Client(_consumer(), token=access_token)
    response = client.request(
            url,
            headers={"Content-Type":"application/x-www-form-urlencoded"}
    )

    return response
