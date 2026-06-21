//! Nug binary format implementation

use super::Nug;
use std::path::PathBuf;

/// Nug binary format specification
pub const NUG_MAGIC: &[u8; 4] = b"NUGX";
pub const NUG_VERSION: u8 = 1;

/// Nug binary header structure
#[derive(Debug, Clone)]
pub struct NugHeader {
    pub magic: [u8; 4],
    pub version: u8,
    pub id_length: u16,
    pub name_length: u16,
    pub version_length: u16,
    pub platform_length: u16,
    pub arch_length: u16,
    pub data_length: u32,
}

impl NugHeader {
    pub fn new() -> Self {
        NugHeader {
            magic: *NUG_MAGIC,
            version: NUG_VERSION,
            id_length: 0,
            name_length: 0,
            version_length: 0,
            platform_length: 0,
            arch_length: 0,
            data_length: 0,
        }
    }
}

/// Create a binary nug from a Nug struct
pub fn create_binary_nug(nug: &Nug, output_path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
    use std::io::Write;
    use base64::{engine::general_purpose, Engine as _};

    let decoded_data = general_purpose::STANDARD.decode(&nug.data)?;

    let mut header = NugHeader::new();
    header.id_length = nug.id.len() as u16;
    header.name_length = nug.name.len() as u16;
    header.version_length = nug.version.len() as u16;
    header.platform_length = nug.platform.len() as u16;
    header.arch_length = nug.arch.len() as u16;
    header.data_length = decoded_data.len() as u32;

    let mut file = std::fs::File::create(output_path)?;

    // Write header
    file.write_all(&header.magic)?;
    file.write_all(&[header.version])?;
    file.write_all(&header.id_length.to_le_bytes())?;
    file.write_all(&header.name_length.to_le_bytes())?;
    file.write_all(&header.version_length.to_le_bytes())?;
    file.write_all(&header.platform_length.to_le_bytes())?;
    file.write_all(&header.arch_length.to_le_bytes())?;
    file.write_all(&header.data_length.to_le_bytes())?;

    // Write strings
    file.write_all(nug.id.as_bytes())?;
    file.write_all(nug.name.as_bytes())?;
    file.write_all(nug.version.as_bytes())?;
    file.write_all(nug.platform.as_bytes())?;
    file.write_all(nug.arch.as_bytes())?;

    // Write binary data
    file.write_all(&decoded_data)?;

    Ok(())
}

/// Parse a binary nug file
pub fn parse_binary_nug(path: &PathBuf) -> Result<Nug, Box<dyn std::error::Error>> {
    use std::io::{Read, Cursor};
    use byteorder::{LittleEndian, ReadBytesExt};
    use base64::{engine::general_purpose, Engine as _};

    let mut file = std::fs::File::open(path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;

    let mut cursor = Cursor::new(buffer);

    // Read header
    let mut magic = [0u8; 4];
    cursor.read_exact(&mut magic)?;
    if magic != *NUG_MAGIC {
        return Err("Invalid nug magic number".into());
    }

    let version = cursor.read_u8()?;
    if version != NUG_VERSION {
        return Err(format!("Unsupported nug version: {}", version).into());
    }

    let id_length = cursor.read_u16::<LittleEndian>()?;
    let name_length = cursor.read_u16::<LittleEndian>()?;
    let version_length = cursor.read_u16::<LittleEndian>()?;
    let platform_length = cursor.read_u16::<LittleEndian>()?;
    let arch_length = cursor.read_u16::<LittleEndian>()?;
    let data_length = cursor.read_u32::<LittleEndian>()?;

    // Read strings
    let mut id = vec![0u8; id_length as usize];
    cursor.read_exact(&mut id)?;
    let mut name = vec![0u8; name_length as usize];
    cursor.read_exact(&mut name)?;
    let mut version_str = vec![0u8; version_length as usize];
    cursor.read_exact(&mut version_str)?;
    let mut platform = vec![0u8; platform_length as usize];
    cursor.read_exact(&mut platform)?;
    let mut arch = vec![0u8; arch_length as usize];
    cursor.read_exact(&mut arch)?;

    // Read binary data
    let mut data = vec![0u8; data_length as usize];
    cursor.read_exact(&mut data)?;
    let encoded_data = general_purpose::STANDARD.encode(&data);

    Ok(Nug {
        id: String::from_utf8(id)?,
        name: String::from_utf8(name)?,
        version: String::from_utf8(version_str)?,
        emoji: None,
        glyph: None,
        ascii: None,
        kind: "binary".to_string(),
        platform: String::from_utf8(platform)?,
        arch: String::from_utf8(arch)?,
        data: encoded_data,
        requires: Vec::new(),
        inputs: Vec::new(),
        outputs: Vec::new(),
        tags: Vec::new(),
        lexicon: None,
        visuals: None,
        resources: None,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;
    use base64::{engine::general_purpose, Engine as _};

    #[test]
    fn test_binary_nug_roundtrip() {
        let original_nug = Nug {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: general_purpose::STANDARD.encode("test binary data"),
            requires: Vec::new(),
            inputs: Vec::new(),
            outputs: Vec::new(),
            tags: Vec::new(),
            lexicon: None,
            visuals: None,
            resources: None,
        };

        let binary_path = PathBuf::from("/tmp/test_nug.bin");
        create_binary_nug(&original_nug, &binary_path).unwrap();

        let parsed_nug = parse_binary_nug(&binary_path).unwrap();
        assert_eq!(parsed_nug.id, "R100-U899");
        assert_eq!(parsed_nug.name, "Runner");
        assert_eq!(parsed_nug.version, "1.0.0");
        assert_eq!(parsed_nug.platform, "linux");
        assert_eq!(parsed_nug.arch, "x86_64");

        std::fs::remove_file(binary_path).unwrap();
    }
}
