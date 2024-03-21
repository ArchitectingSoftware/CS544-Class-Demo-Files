use color_eyre::eyre::Result;
use s2n_quic::{client::Connect, Client};
use std::{path::Path, net::SocketAddr};
use std::net::ToSocketAddrs;

use crate::protocol::echo::{EchoProtocol, MSG_TYPE_DATA};

#[derive(Debug)]
struct ClientOptions{
  address: String,
  port: u16,
  cert: String,
}

#[tokio::main]
async fn run(options:ClientOptions) -> Result<()> {
    let host_port_string = format!("{}:{}", 
      options.address, options.port).to_socket_addrs()?.next().unwrap();

    let addr: SocketAddr = "0.0.0.0:0".parse()?;
    let client = Client::builder()
        .with_tls(Path::new(&options.cert))?
        .with_io(addr)?
        .start()?;

    println!("Connecting client...");
    let connect = Connect::new(host_port_string).with_server_name("localhost");
    let mut connection = client.connect(connect).await?;

    println!("Client connected...");
    // ensure the connection doesn't time out with inactivity
    connection.keep_alive(true)?;

    // open a new stream and split the receiving and sending sides
    let stream = connection.open_bidirectional_stream().await?;
    let (mut receive_stream, mut send_stream) = stream.split();

    //YOUR APPLICATION PROTOCOL STARTS HERE
    
    //STEP 1: Send a message to the server
    let msg = EchoProtocol::new(MSG_TYPE_DATA, "Hello, world!".to_string());
    //println!("<== TO SERVER ==\n {} \n===", msg.to_json().unwrap());  
    msg.print_debug_msg("TO SERVER");
    let data = msg.to_bytes().unwrap();
    send_stream.send(data.into()).await.expect("stream should be open");
    

    //STEP 2: Receive a message from the server
    let rdata =  receive_stream.receive().await.expect("stream should be open").unwrap();
    let result = EchoProtocol::from_bytes(rdata.to_vec()).unwrap();
    result.print_debug_msg("FROM SERVER");
    
    Ok(())
}


pub fn do_client(address: String, port: u16, cert: String) -> Result<()> {
  println!("Starting client...");
  println!("Connecting to {address} on port {port}...");

  let options = ClientOptions {
    address,
    port,
    cert,
  };

  run(options)?;

  Ok(())
}
