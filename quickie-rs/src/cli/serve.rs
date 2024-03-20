use color_eyre::eyre::Result;

pub fn do_serve(address: String, port: u16) -> Result<()> {
  println!("Starting server...");
  println!("Listening on {address} using port {port}...");

  Ok(())
}
