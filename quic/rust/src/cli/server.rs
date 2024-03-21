use color_eyre::eyre::Result;
use s2n_quic::Server;
use std::{path::Path};
use std::net::ToSocketAddrs;

use crate::protocol::echo::{EchoProtocol, MSG_TYPE_ACK};
#[derive(Debug)]
struct ServerOptions{
  address: String,
  port: u16,
  cert: String,
  key: String,
}

#[tokio::main]
async fn run(options: ServerOptions) -> Result<()>  {

  let host_port_string = format!("{}:{}", 
    options.address, options.port).to_socket_addrs()?.next().unwrap();
  let mut server = Server::builder()
        .with_tls((Path::new(&options.cert), Path::new(&options.key)))?
        .with_io(host_port_string)?
        .start()?;
  println!{"{:#?} In server...", options}
  while let Some(mut connection) = server.accept().await {
    // spawn a new task for the connection
    tokio::spawn(async move {
        while let Ok(Some(mut stream)) = connection.accept_bidirectional_stream().await {
            // spawn a new task for the stream
            tokio::spawn(async move {
                // echo any data back to the stream
                while let Ok(Some(data)) = stream.receive().await {
                    let mut result = EchoProtocol::from_bytes(data.to_vec()).unwrap();
                    result.print_debug_msg("FROM CLIENT");
                    
                    //Build response message
                    let respmsg = format!{"Echo {}", result.msg.to_string()};
                    result.msg = respmsg;
                    result.mtype |=  MSG_TYPE_ACK;

                    //Now send the response
                    let data = result.to_bytes().unwrap();
                    result.print_debug_msg("TO CLIENT");
                    let payload = data.into();
                    stream.send(payload).await.expect("stream should be open");
                }
            });
        }
    });
  }
  Ok(())
}

pub fn do_server(address: String, port: u16, cert:String, key:String) -> Result<()> {
  println!("Starting server...");
  println!("Listening on {address} using port {port}...");

  let options = ServerOptions {
    address,
    port,
    cert,
    key,
  };

  run(options)?;

  // return Ok if there is no error
  Ok(())
}
