use color_eyre::eyre::{eyre, Result, WrapErr};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
pub struct Message {
  version: isize,
  length: usize,
}

impl Message {
  pub fn new(version: isize, length: usize) -> Self {
    Self { length, version }
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
    Ok(self.to_json()?.as_bytes().to_owned())
  }

  pub fn to_json(&self) -> Result<String> {
    let pretty_json = serde_json::to_string_pretty(self)
      .wrap_err_with(|| eyre!("Problem serializing Message to JSON"))?;

    Ok(pretty_json)
  }

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
    let message = Message::new(1, 42);

    assert_eq!(message.version, 1);
  }
}
