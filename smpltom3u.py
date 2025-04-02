#!/usr/bin/env python3
import sys
import os
import json
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3

def smpl_to_m3u8_content(input_file):
    """
    Reads the SMPL file (JSON format), and converts it to an M3U8-format string.
    """
    with open(input_file, 'r') as f:
        content = f.read()
    data = json.loads(content)
    # Build the m3u8 content using the "info" field from each song.
    m3u8_content = "#EXTM3U\n"
    for song in data["members"]:
        m3u8_content += song["info"] + "\n"
    return m3u8_content

def get_metadata(file_path):
    """
    Extracts duration (in seconds), artist and title from the audio file.
    Returns (duration:int, "Artist - Title") or defaults if unavailable.
    """
    try:
        audio = MutagenFile(file_path, easy=True)
        if audio is None:
            raise Exception("Unsupported format or unreadable file.")
        duration = int(audio.info.length) if audio.info and audio.info.length else -1
        artist = audio.get('artist', ['Unknown Artist'])[0]
        title = audio.get('title', [os.path.splitext(os.path.basename(file_path))[0]])[0]
        return duration, f"{artist} - {title}"
    except Exception as e:
        return -1, f"Unknown Artist - {os.path.splitext(os.path.basename(file_path))[0]}"

def parse_media_paths(lines):
    """
    Filters out blank and comment lines from a list of lines.
    """
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]

def m3u8_content_to_m3u(m3u8_content):
    """
    Converts an M3U8-format string (without metadata) to an M3U-format string with metadata.
    """
    lines = m3u8_content.splitlines()
    # Remove BOM from the first line if present.
    if lines and lines[0].startswith('\ufeff'):
        lines[0] = lines[0].lstrip('\ufeff')
    media_paths = parse_media_paths(lines)
    
    # Start the final M3U content.
    m3u_content = "#EXTM3U\n\n"
    for path in media_paths:
        duration, description = get_metadata(path)
        m3u_content += f"#EXTINF:{duration},{description}\n"
        m3u_content += f"{path}\n\n"
    return m3u_content

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <playlist.smpl>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    # Convert the SMPL file to an in-memory M3U8 string.
    m3u8_content = smpl_to_m3u8_content(input_file)
    # Process the M3U8 string to generate the final M3U content.
    m3u_content = m3u8_content_to_m3u(m3u8_content)
    
    # Determine output file name (same base, .m3u extension)
    base, _ = os.path.splitext(input_file)
    output_file = base + ".m3u"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"Successfully converted '{input_file}' to '{output_file}'.")

if __name__ == "__main__":
    main()
