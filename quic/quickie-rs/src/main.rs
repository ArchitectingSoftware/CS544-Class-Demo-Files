use color_eyre::eyre::{eyre, Result};

mod cli;

pub(crate) mod protocol{
  pub mod echo;
}


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

  let cert = matches
    .get_one::<String>("cert")
    .ok_or_else(|| eyre!("unable to extract address cert arg"))?
    .to_owned();

  let key = matches
    .get_one::<String>("key")
    .ok_or_else(|| eyre!("unable to extract address key arg"))?
    .to_owned();

  match matches.subcommand() {
    Some(("client", _client_matches)) => cli::client::do_client(address, port, cert),
    Some(("server", _server_matches)) => cli::server::do_server(address, port, cert, key),
    Some((unknown, _unknown_matches)) => {
      unreachable!("Unknown subcommands aren't allowed but got {unknown}.")
    }
    None => unreachable!("Subcommands are required."),
  }
}
