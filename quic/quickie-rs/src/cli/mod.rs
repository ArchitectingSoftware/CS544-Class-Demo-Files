use clap::{command, value_parser, Arg, ArgMatches, Command};

pub(crate) mod client;
pub(crate) mod server;


pub(crate) fn get_cli_matches() -> ArgMatches {
  let shared_address_arg = Arg::new("address")
    .value_parser(value_parser!(String))
    .global(true)
    .short('a')
    .long("address")
    .value_name("IP_ADDRESS")
    .env("ADDRESS")
    .default_value("0.0.0.0")
    .help("address to use for connections");

  let shared_port_arg = Arg::new("port")
    .value_parser(value_parser!(u16))
    .global(true)
    .short('p')
    .long("port")
    .value_name("PORT")
    .env("PORT")
    .help("port to use for connections")
    .default_value("54321");

  let shared_cert_arg = Arg::new("cert")
    .value_parser(value_parser!(String))
    .global(true)
    .short('c')
    .long("cert")
    .value_name("CERT_FILE")
    .env("CERT_FILE")
    .default_value("./certs/quicrs.crt")
    .help("certificate file connections");

  let shared_key_arg = Arg::new("key")
    .value_parser(value_parser!(String))
    .global(true)
    .short('k')
    .long("key")
    .value_name("KEY_FILE")
    .env("KEY_FILE")
    .default_value("./certs/quicrs.key")
    .help("certificate file connections");

  command!()
    .about(env!("CARGO_PKG_DESCRIPTION"))
    .author(env!("CARGO_PKG_AUTHORS"))
    .version(env!("CARGO_PKG_VERSION"))
    .arg_required_else_help(true)
    .help_expected(true)
    .propagate_version(true)
    .subcommand_required(true)
    .arg(shared_address_arg)
    .arg(shared_port_arg)
    .arg(shared_cert_arg)
    .arg(shared_key_arg)
    .subcommand(Command::new("client").about("Start a client"))
    .subcommand(Command::new("server").about("Start a server"))
    .get_matches()
}
