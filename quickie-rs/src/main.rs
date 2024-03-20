use color_eyre::eyre::{eyre, Result};

mod cli;
mod message;

fn main() -> Result<()> {
  color_eyre::install()?;

  let matches = cli::get_cli_matches();
  println!("Hello, world!");

  let port = matches
    .get_one::<u16>("port")
    .ok_or_else(|| eyre!("unable to extract port CLI arg"))?
    .to_owned();

  let address = matches
    .get_one::<String>("address")
    .ok_or_else(|| eyre!("unable to extract address CLI arg"))?
    .to_owned();

  match matches.subcommand() {
    Some(("client", _client_matches)) => cli::client::do_client(address, port),
    Some(("serve", _serve_matches)) => cli::serve::do_serve(address, port),
    Some((unknown, _unknown_matches)) => {
      unreachable!("Unknown subcommands aren't allowed but got {unknown}.")
    }
    None => unreachable!("Subcommands are required."),
  }
}
