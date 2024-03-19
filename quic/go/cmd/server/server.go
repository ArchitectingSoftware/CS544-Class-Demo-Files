package main

import (
	"context"
	"crypto/tls"
	"flag"
	"log"

	"github.com/quic-go/quic-go"

	crypto_cfg "drexel.edu/net-quic/pkg/crypto"
	"drexel.edu/net-quic/pkg/pdu"
)

var (
	GENERATE_TLS = true
	CERT_FILE    = ""
	KEY_FILE     = ""
)

func processFlags() {
	flag.BoolVar(&GENERATE_TLS, "generate-tls", GENERATE_TLS, "generate new TLS certificate")
	flag.StringVar(&CERT_FILE, "cert-file", CERT_FILE, "TLS certificate file")
	flag.StringVar(&KEY_FILE, "key-file", KEY_FILE, "TLS key file")
	flag.Parse()
}

func getTLS() *tls.Config {
	///tlsConfig := &tls.Config{}

	if GENERATE_TLS {
		tlsConfig, err := crypto_cfg.GenerateTLSConfig()
		if err != nil {
			log.Fatal(err)
		}
		return tlsConfig
	} else {
		tlsConfig, err := crypto_cfg.BuildTLSConfig(CERT_FILE, KEY_FILE)
		if err != nil {
			log.Fatal(err)
		}
		return tlsConfig
	}
}

func main() {
	processFlags()

	tlsConfig := getTLS()
	ctx := context.TODO()

	listener, err := quic.ListenAddr("localhost:4242", tlsConfig, nil)
	if err != nil {
		log.Fatal(err)
	}
	for {
		log.Println("Accepting new session")
		sess, err := listener.Accept(ctx)
		if err != nil {
			log.Fatal(err)
		}
		go func() {
			for {
				stream, err := sess.AcceptStream(ctx)
				log.Println("Connect client stream")
				if err != nil {
					log.Print("Accept: ", err)
					break
				}

				go func(stream quic.Stream) {
					buf := make([]byte, 100)
					n, err := stream.Read(buf)
					if err != nil {
						log.Fatal("Write:", err)
					}
					data, _ := pdu.PduFromBytes(buf[:n])

					log.Printf("Server got: [%s] %s",
						data.GetTypeAsString(), data.GetData())

					data.SetType(pdu.TYPE_ACK)
					data.SetData("ack: FromServer Echo-" + data.GetData())
					rsp := pdu.PduToBytes(data)

					_, err = stream.Write(rsp)
					if err != nil {
						log.Fatal("Write:", err)
					}
				}(stream)
			}
		}()
	}

}
