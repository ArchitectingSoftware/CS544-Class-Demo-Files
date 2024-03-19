package main

import (
	"context"
	"flag"
	"log"

	"github.com/quic-go/quic-go"

	crypto_cfg "drexel.edu/net-quic/pkg/crypto"
	"drexel.edu/net-quic/pkg/pdu"
)

var (
	ADDRESS = "localhost:4242"
)

func processFlags() {
	flag.StringVar(&ADDRESS, "address", ADDRESS, "address to listen on")
	flag.Parse()
}

func simpleRequest(msg string) *pdu.PDU {
	return pdu.NewPDU(pdu.TYPE_DATA, msg)
}

func main() {
	processFlags()

	tlsConfig := crypto_cfg.BuildTLSClientConfig()
	ctx := context.TODO()

	conn, err := quic.DialAddr(ctx, ADDRESS, tlsConfig, nil)
	if err != nil {
		log.Fatal(err)
	}
	stream, err := conn.OpenStreamSync(ctx)
	if err != nil {
		log.Fatal(err)
	}

	req := simpleRequest("hello")
	pduBytes := pdu.PduToBytes(req)
	log.Printf("raw data: %v", pduBytes)
	_, err = stream.Write(pduBytes)
	if err != nil {
		log.Fatal(err)
	}
	buf := make([]byte, 100)
	n, err := stream.Read(buf)
	if err != nil {
		log.Fatal(err)
	}
	rsp, _ := pdu.PduFromBytes(buf[:n])
	log.Printf("Client got: [%s] %s",
		rsp.GetTypeAsString(), rsp.GetData())
}
