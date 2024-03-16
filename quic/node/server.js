const { createQuicSocket } = require('net');
const { readFileSync } = require('fs');


const server = createQuicSocket({
    endpoint: {
        address: "127.0.0.1",
        port: 1234,
    },
    //certificate: readFileSync('cert.pem'),
    key: readFileSync('./public_key.pem')
});

server.on('session', (session) => {
    session.on('stream', (stream) => {
        stream.end('hello');
    });
});

server.listen();

