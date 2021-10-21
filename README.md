# Backup

Backup utilies.

# Development

Install poetry
```bash
pip3 install 'poetry>=1.2.0a2' --user
```

Install dependencies:
```bash
poetry install
```

## Proxy configuration

If you're working under a proxy, make sure to add it in your environment:
```bash
export HTTP_PROXY=proxy.example.com:8080
export HTTPS_PROXY=proxy.example.com:8080
```

If you're working under a TLS termination proxy, you will need the following:
```bash
# For RHEL
export REQUESTS_CA_BUNDLE=/etc/pki/tls/cert.pem
# For Ubuntu
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
