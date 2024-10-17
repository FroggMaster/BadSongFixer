# BadSongFixer
Tool designed to review notes.mid files for YARG/Clone Hero and correct ambigous title meta-data. 

## Features
- Renames the first track (`Track 1`) to the format: `Artist - Song Name` based on the `song.ini` file.
- Validates track names against a list of allowed titles and their numbered variations.
- Removes invalid track titles only if there are multiple titles on a track.
- Creates a backup of the original `notes.mid` file before saving any changes.
- The script echoes key information during processing, such as:
  - The current and new title of `Track 1`.
  - Any invalid track titles found and whether they are removed.
  - Renaming of `notes.mid` to `notes.mid.old` if changes are made.
  - Warnings for tracks with no titles
  - If no changes are necessary, the script will indicate that the file is already valid.

## Usage

### Prerequisites
- Python 3.x
- `mido` library for MIDI file handling (`pip install mido`)

### Command-line Arguments

1. **Single Song Directory Processing**

   Process a single directory containing `notes.mid` and `song.ini`.

   ```bash
   python badsongfix.py --dir "<path_to_song_directory>"
   ```

2. **Multiple Song Directory Processing**

   Process multiple directories listed in a text file. Each directory path should be on a new line.

   ```bash
   python badsongfix.py --list "<song_directory_list.txt>"
   ```
   For processing multiple directories, you can create a text file with a list of directories. Each line in this file should contain the full path to a song directory that contains both `notes.mid` and `song.ini`. The format for the directory list text file should look like this:
   ```
   C:\Users\Frog\Songs\Rock Band 2 DLC\Alice In Chains - No Excuses\
   C:\Users\Frog\Songs\Rock Band 2 DLC\Alice In Chains - Rooster\
   C:\Users\Frog\Songs\Rock Band 2 DLC\Alice In Chains - Would\
   C:\Users\Frog\Songs\Rock Band 2 DLC\Elvis Costello - Radio Radio\
   ```

	Each directory path must be listed on a new line.
