#!/usr/bin/python

''' a simple tool to print example output of an API in pretty format 
    
    Usage: 
        python print_api.py <method> <function> <parms> -t<access_token>
        
        parms should be quoted, for example: 
            'a=1&foo=bar&b=10&pageSize=5' 
        and so on.

'''
import py7D
import json
from pprint import pprint
import argparse

def print_api(method, function, access_token, **kwargs):
    if access_token:
        rc = py7D.oauth_request(method,
                                function,
                                access_token,
                                **kwargs)
    else:
        rc = py7D.request(method, function, **kwargs)

    pprint(rc['http_headers'])
    print json.dumps(rc['response'], indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="print_api <method> <function> <parms> -t<access_token>")
    parser.add_argument("method", type=str)
    parser.add_argument("function", type=str, default=None)
    parser.add_argument("-t", type=str, default=None, dest='access_token')
    parser.add_argument("parms", type=str, default='')
    args = parser.parse_args()
    qparms = args.parms.split('&')
    kwargs = {}
    for pair in qparms:
        k,v = pair.split('=')
        kwargs[k] = v
    print_api(args.method, args.function, args.access_token, **kwargs)
