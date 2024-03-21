use color_eyre::eyre::{eyre, Result, WrapErr};
use serde::{Deserialize, Serialize};

pub const PROTO_VERSION: u8 = 0x01;
pub const MSG_TYPE_DATA:u8 = 0x01;
pub const MSG_TYPE_ACK:u8 = 0x02;

#[derive(Debug, Deserialize, Serialize)]
pub struct EchoProtocol {
  ver: u8,
  pub mtype: u8,
  pub msg: String,
}

impl EchoProtocol {
  pub fn new(mtype: u8, msg: String) -> Self {
    EchoProtocol { ver:PROTO_VERSION, mtype, msg }
  }

  pub fn from_json(raw: &str) -> Result<Self> {
    let message = serde_json::from_str(raw)?;

    Ok(message)
  }

  pub fn from_bytes(raw: Vec<u8>) -> Result<Self> {
    let raw_json =
      String::from_utf8(raw).wrap_err_with(|| eyre!("Unable to parse bytes as UTF8 string"))?;

    Ok(Self::from_json(&raw_json)?)
  }

  pub fn to_bytes(&self) -> Result<Vec<u8>> {
    // Implement binary bits here
    //Ok(self.to_json()?.as_bytes().to_owned())
    Ok(self.to_json()?.into_bytes())
  }

  pub fn to_json(&self) -> Result<String> {
    let pretty_json = serde_json::to_string_pretty(self)
      .wrap_err_with(|| eyre!("Problem serializing Message to JSON"))?;

    Ok(pretty_json)
  }
  // Define a method for future use
  #[allow(dead_code)]
  pub fn print_debug_msg(&self, msg: &str) {
    println!("<============ {}\n {} \n==============", 
      msg, self.to_json().unwrap()); 
  }

  // Define a method for future use
  #[allow(dead_code)]
  pub fn to_string(&self) -> String {
    format!("{:#?}", self)
  }
}



#[cfg(test)]
mod tests {
  use super::*;

  use pretty_assertions::assert_eq;

  #[test]
  fn constructor_sanity() {
    let message = EchoProtocol::new(1, 
      "Hello, world!".to_string());

    assert_eq!(message.mtype, 1);
  }
}
