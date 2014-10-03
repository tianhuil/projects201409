# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 17:06:08 2014

@author: eyalshiv
"""






import oauth2 as oauth


def get_song_url(song_id):

    consumer_key = '7drussrakh7t'
    consumer_secret = 'fr4sykcr47ryd8te'
    consumer = oauth.Consumer(consumer_key, consumer_secret)


    request_url = "http://previews.7digital.com/clip/" + song_id
    

    req = oauth.Request(method="GET", url=request_url,is_form_encoded=True)

    req['oauth_timestamp'] = oauth.Request.make_timestamp()
    req['oauth_nonce'] = oauth.Request.make_nonce()
    sig_method = oauth.SignatureMethod_HMAC_SHA1()

    req.sign_request(sig_method, consumer, token=None)

    return req.to_url()
    
    
    