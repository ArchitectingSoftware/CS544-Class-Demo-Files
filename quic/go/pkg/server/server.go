package server

import (
	"context"
	"crypto/tls"
	"fmt"
	"log"

	"drexel.edu/net-quic/pkg/pdu"
	"drexel.edu/net-quic/pkg/util"
	"github.com/quic-go/quic-go"
)

type ServerConfig struct {
	GenTLS   bool
	CertFile string
	KeyFile  string
	Address  string
	Port     int
}

type Server struct {
	cfg ServerConfig
	tls *tls.Config
	ctx context.Context
}

func NewServer(cfg ServerConfig) *Server {
	server := &Server{
		cfg: cfg,
	}
	server.tls = server.getTLS()
	server.ctx = context.TODO()
	return server
}

func (s *Server) getTLS() *tls.Config {
	if s.cfg.GenTLS {
		tlsConfig, err := util.GenerateTLSConfig()
		if err != nil {
			log.Fatal(err)
		}
		return tlsConfig
	} else {
		tlsConfig, err := util.BuildTLSConfig(s.cfg.CertFile, s.cfg.KeyFile)
		if err != nil {
			log.Fatal(err)
		}
		return tlsConfig
	}
}

func (s *Server) Run() error {
	address := fmt.Sprintf("%s:%d", s.cfg.Address, s.cfg.Port)
	listener, err := quic.ListenAddr(address, s.tls, nil)
	if err != nil {
		log.Printf("error listening: %s", err)
		return err
	}

	//SERVER LOOP
	for {
		log.Println("Accepting new session")
		sess, err := listener.Accept(s.ctx)
		if err != nil {
			log.Printf("error accepting: %s", err)
			return err
		}

		go s.streamHandler(sess)
	}
}

func (s *Server) streamHandler(sess quic.Connection) {
	for {
		log.Print("[server] waiting for client to open stream")
		stream, err := sess.AcceptStream(s.ctx)
		if err != nil {
			log.Printf("[server] stream closed: %s", err)
			break
		}

		//Handle protocol activity on stream
		s.protocolHandler(stream)
	}
}

func (s *Server) protocolHandler(stream quic.Stream) error {
	//THIS IS WHERE YOU START HANDLING YOUR APP PROTOCOL
	buff := pdu.MakePduBuffer()

	n, err := stream.Read(buff)
	if err != nil {
		log.Printf("[server] Error Reading Raw Data: %s", err)
		return err
	}

	data, err := pdu.PduFromBytes(buff[:n])
	if err != nil {
		log.Printf("[server] Error decoding PDU: %s", err)
		return err
	}

	log.Printf("[server] Data In: [%s] %s",
		data.GetTypeAsString(), string(data.Data))

	//Now lets echo it back
	rspMsg := fmt.Sprintf("ack: FromServer Echo-%s",
		string(data.Data))

	rspPdu := pdu.PDU{
		Mtype: pdu.TYPE_DATA | pdu.TYPE_ACK,
		Len:   uint32(len(rspMsg)),
		Data:  []byte(rspMsg),
	}

	rspBytes, err := pdu.PduToBytes(&rspPdu)
	if err != nil {
		log.Printf("[server] Error encoding PDU: %s", err)
		return err
	}

	_, err = stream.Write(rspBytes)
	if err != nil {
		log.Printf("[server] Error sending response: %s", err)
		return err
	}
	return nil
}
