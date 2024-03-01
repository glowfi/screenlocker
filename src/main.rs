use std::fs::File;
use std::io::Write;
use std::process::Command;
use std::{env, fs};
use tempfile::NamedTempFile;

// Constants
const AUDIO_FILE_1: &[u8] = include_bytes!("./lock.ogg");
const AUDIO_FILE_2: &[u8] = include_bytes!("./unlock.ogg");
const AUDIO_FILE_3: &[u8] = include_bytes!("./wrong.ogg");
const PYTHON_SCRIPT: &str = include_str!("./screenLock.py");
const JSON: &str = include_str!("./vid.json");

fn main() {
    // Create three temporary files and write the embedded audio data to them
    let mut temp_file_1 = NamedTempFile::new().expect("failed to create temp file");
    let mut temp_file_2 = NamedTempFile::new().expect("failed to create temp file");
    let mut temp_file_3 = NamedTempFile::new().expect("failed to create temp file");
    temp_file_1
        .write_all(AUDIO_FILE_1)
        .expect("failed to write temp file");
    temp_file_2
        .write_all(AUDIO_FILE_2)
        .expect("failed to write temp file");
    temp_file_3
        .write_all(AUDIO_FILE_3)
        .expect("failed to write temp file");

    // Get the paths to the temporary files and set them as environment variables
    let temp_file_path_1 = temp_file_1
        .path()
        .to_str()
        .expect("failed to get temp file path");
    let temp_file_path_2 = temp_file_2
        .path()
        .to_str()
        .expect("failed to get temp file path");
    let temp_file_path_3 = temp_file_3
        .path()
        .to_str()
        .expect("failed to get temp file path");
    env::set_var("AUDIO_FILE_PATH_1", temp_file_path_1);
    env::set_var("AUDIO_FILE_PATH_2", temp_file_path_2);
    env::set_var("AUDIO_FILE_PATH_3", temp_file_path_3);

    // Write the embedded Python file to a temporary file
    let mut temp_file = File::create("temp.py").expect("failed to create temp file");
    temp_file
        .write_all(PYTHON_SCRIPT.as_bytes())
        .expect("failed to write temp file");

    // Write the embedded JSON to a temporary file

    let mut temp_file_json = NamedTempFile::new().expect("failed to create temp file");
    temp_file_json
        .write_all(JSON.as_bytes())
        .expect("failed to write temp file");

    let temp_file_path_json = temp_file_json
        .path()
        .to_str()
        .expect("failed to get temp file path");
    env::set_var("JSON_FILE_PATH", temp_file_path_json);

    // Run the Python script using the temporary file
    let output = Command::new("python")
        .arg("temp.py")
        .output()
        .expect("failed to execute process");

    // Clean up the temporary files
    temp_file_1.close().expect("failed to delete temp file");
    temp_file_2.close().expect("failed to delete temp file");
    temp_file_3.close().expect("failed to delete temp file");
    temp_file_json.close().expect("failed to delete temp file");
    let __ = fs::remove_file("temp.py");

    // Print to Stdout
    println!("Output: {:?}", String::from_utf8_lossy(&output.stdout));
    println!("Errors: {:?}", String::from_utf8_lossy(&output.stderr));
}
