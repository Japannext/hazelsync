'''Some utils functions'''

import os
from pathlib import Path

def seq_run(functions):
    '''Run a list of functions sequentially'''
    results = []
    for func, args in functions:
        results.append(func(*args))
    return results

def async_run(functions):
    '''Run a list of functions in async'''
    raise NotImplementedError()

CA_BUNDLE_PATHS = [
    '/etc/ssl/certs/ca-certificates.crt', # Debian / Ubuntu / Gentoo
    '/etc/pki/tls/certs/ca-bundle.crt', # RHEL 6
    '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem', # RHEL 7
    '/etc/ssl/ca-bundle.pem', # OpenSUSE
    '/etc/pki/tls/cacert.pem', # OpenELEC
    '/etc/ssl/cert.pem', # Alpine Linux
]

def ca_bundle():
    '''Returns Linux CA bundle path'''
    if os.environ.get('SSL_CERT_FILE'):
        return os.environ.get('SSL_CERT_FILE')
    if os.environ.get('REQUESTS_CA_BUNDLE'):
        return os.environ.get('REQUESTS_CA_BUNDLE')
    for ca_path in CA_BUNDLE_PATHS:
        if Path(ca_path).exists():
            return ca_path
    return None
