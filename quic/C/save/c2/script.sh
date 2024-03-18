#!/bin/bash
New-SelfSignedCertificate -DnsName $env:computername,localhost -FriendlyName QuicInteropServer -KeyUsageProperty Sign -KeyUsage DigitalSignature -CertStoreLocation cert:\CurrentUser\My -HashAlgorithm SHA256 -Provider "Microsoft Software Key Storage Provider"

openssl req  -nodes -new -x509  -keyout server.key -out server.cert

openssl genrsa -out ca.key 2048  openssl req -new -key ca.key -out ca.csr openssl x509 -req -days 365 -in ca.csr -signkey ca.key -out ca.crt