#!/bin/bash
openssl genpkey -algorithm RSA -aes256 -pass pass:drexelnetworking  \
-out private_key.pem \
-config certificate.conf

openssl rsa -pubout -in private_key.pem -out public_key.pem -passin pass:drexelnetworking
