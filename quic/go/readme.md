## Simple Go Echo Demo using QUIC

There are 2 executables:

- `cmd/client`: `go run client.go`
- `cmd/server`: `go run server.go`

The server will wait for a connection, just a simple echo.  This solution uses goroutines and is concurrent.

There is also a pdu defined in the `pkg/pdu` package

Solution derived from the excellent work of the `quic-go` team based on the example: https://github.com/quic-go/quic-go/tree/master/example/echo