## Simple Go Echo Demo using QUIC

There is a single binary that is used to run both the client and the server

- `server`: `go run cmd/echo/echo.go -server`
- `client`: `go run cmd/echo/echo.go -client`
- `help on all flags`: `go run cmd/echo/echo.go -help`

The server will wait for a connection, just a simple echo.  This solution uses goroutines and is concurrent.

There is also a pdu defined in the `pkg/pdu` package

Solution derived from the excellent work of the `quic-go` team based on the example: https://github.com/quic-go/quic-go/tree/master/example/echo