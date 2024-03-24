package util

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"log"
	"math/big"
	"os"
)

func BuildTLSClientConfig() *tls.Config {
	return &tls.Config{
		InsecureSkipVerify: true,
		NextProtos:         []string{"quic-echo-example"},
	}
}

func BuildTLSClientConfigWithCert(certFile string) (*tls.Config, error) {
	caCert, err := os.ReadFile(certFile)
	if err != nil {
		log.Println("[client] error reading server certificate:", err)
		return nil, fmt.Errorf("error reading server certificate: %w", err)
	}

	// Parse the certificate
	caCertPool := x509.NewCertPool()
	caCertPool.AppendCertsFromPEM(caCert)

	// Create a tls.Config object with the server's certificate
	return &tls.Config{
		RootCAs:    caCertPool,
		NextProtos: []string{"quic-echo-example"},
	}, nil
}

func BuildTLSConfig(cert string, key string) (*tls.Config, error) {
	tlsCert, err := tls.LoadX509KeyPair(cert, key)
	if err != nil {
		return nil, err
	}

	return &tls.Config{
		Certificates: []tls.Certificate{tlsCert},
		NextProtos:   []string{"quic-echo-example"},
	}, nil
}

func GenerateTLSConfig() (*tls.Config, error) {
	key, err := rsa.GenerateKey(rand.Reader, 1024)
	if err != nil {
		return nil, err
	}
	template := x509.Certificate{SerialNumber: big.NewInt(1)}
	certDER, err := x509.CreateCertificate(rand.Reader, &template, &template, &key.PublicKey, key)
	if err != nil {
		return nil, err
	}
	keyPEM := pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(key)})
	certPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: certDER})

	tlsCert, err := tls.X509KeyPair(certPEM, keyPEM)
	if err != nil {
		return nil, err
	}
	return &tls.Config{
		Certificates: []tls.Certificate{tlsCert},
		NextProtos:   []string{"quic-echo-example"},
	}, nil
}
