use color_eyre::eyre::Result;

pub fn do_client(address: String, port: u16) -> Result<()> {
  println!("Starting client...");
  println!("Connecting to {address} on port {port}...");

  Ok(())
}
