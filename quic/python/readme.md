## Python QUIC Shell

1. Install dependencies with pip (requirements.txt) is provided
2. The certs in the ./certs directory are fine for testing there is a script if you want to rebuild your own but you will need openssl installed
3. run `python3 echo.py server` to start the server with defaults and `python3 echo.py client` to start the client with defaults.

Correct output for server:

```sh
(.venv) ➜  python git:(main) ✗ python3 echo.py server
[svr] Server starting...
[svr] received message:  This is a test message
```

Correct output for client:


```sh
(.venv) ➜  python git:(main) ✗ python3 echo.py client
[cli] starting client
[cli] got message:  SVR-ACK: This is a test message
[cli] msg as json:  {"mtype": 1, "msg": "SVR-ACK: This is a test message", "sz": 31}
```