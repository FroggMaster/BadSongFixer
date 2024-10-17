import mido
import configparser
import os
import argparse
import re

# List of valid track titles (base form without numbering)
VALID_TITLES = [
    "PART DRUMS", "PART BASS", "PART GUITAR", "PART VOCALS", 
    "EVENTS", "VENUE", "BEAT", 
    "PART REAL_GUITAR_22", "PART REAL_GUITAR", "PART REAL_BASS", 
    "PART KEYS", "PART REAL_KEYS_X", "PART REAL_KEYS_H", 
    "PART REAL_KEYS_E", "PART REAL_KEYS_M", "PART KEYS_ANIM_RH", 
    "PART KEYS_ANIM_LH", "HARM"
]

# Function to create a regex pattern from the VALID_TITLES list
def create_valid_title_pattern():
    # Escape any special characters in the titles and join them into a regex pattern
    escaped_titles = [re.escape(title) for title in VALID_TITLES]
    pattern = r'^(?:' + '|'.join(escaped_titles) + r')(_?\d*)?$'  # Allow optional increment
    return re.compile(pattern)

# Function to parse the song.ini file and get the song name and artist
def get_song_info(ini_file):
    config = configparser.ConfigParser()
    config.read(ini_file)

    # The values are under the "song" section, so we fetch them from there
    if 'song' in config:
        song_name = config.get('song', 'name', fallback=None)
        artist = config.get('song', 'artist', fallback=None)
    else:
        song_name = None
        artist = None
    
    return song_name, artist

# Function to check if a title is valid, including numbered variations
def is_valid_title(title):
    pattern = create_valid_title_pattern()  # Get the dynamic regex pattern
    return bool(pattern.match(title))

# Function to modify the MIDI file
def modify_midi(file_path, song_name, artist):
    # Echo the MIDI file being changed
    print(f"Modifying MIDI file: {file_path}")

    # Load the MIDI file
    midi = mido.MidiFile(file_path)

    # Track whether track 1 needs to be modified
    track1_modified = False
    new_name = f"{artist} - {song_name}"  # Set the new title
    changes_made = False  # Flag to track if any changes were made

    if len(midi.tracks) > 0:
        first_track = midi.tracks[0]
        
        # Check the current name of Track 1
        old_name = first_track.name
        print(f"Current Track 1 title: '{old_name}'")

        # Set Track 1's title if it's blank or has a specific value
        if old_name == "":
            first_track.name = new_name  # Rename track 1 to the expected name
            track1_modified = True
            changes_made = True
            print(f"Track 1 title was blank. Set to: '{new_name}'")  # Log the change
        elif old_name == "midi_export":  # Check if the first track's name is "midi_export"
            first_track.name = new_name  # Rename track 1
            track1_modified = True
            changes_made = True
            print(f"Track 1 title changed: From '{old_name}' To '{new_name}'")  # Log the change
        elif old_name == new_name:
            print(f"Track 1 title '{old_name}' matches the new title. No change needed.")
        else:
            print(f"Track 1 title '{old_name}' does not match expected title. No change needed.")

    # Keep track of invalid titles found in all tracks
    invalid_titles_found = False

    # Process all tracks to find titles
    for i, track in enumerate(midi.tracks):
        valid_titles_found = []
        titles_found = []  # Keep track of titles found

        for msg in track:
            if msg.type == 'track_name':
                titles_found.append(msg.name)  # Collect all track titles
                if is_valid_title(msg.name) or msg.name == new_name:  # Allow new_name as valid
                    valid_titles_found.append(msg)
                else:
                    invalid_titles_found = True  # Mark if there's an invalid title

        # Echo the title of Track 1 explicitly
        if i == 0:
            if valid_titles_found:
                print(f"Track 1 title found: {valid_titles_found[0].name}")
            else:
                print(f"Track 1 has no valid title.")

        # Log valid titles found in each track
        if valid_titles_found:
            print(f"Valid titles found in Track {i + 1}: {', '.join(msg.name for msg in valid_titles_found)}")
        else:
            if len(titles_found) == 0:
                print(f"Warning: Track {i + 1} has no titles at all.")
            elif len(titles_found) > 1:
                print(f"Warning: Track {i + 1} has titles but they are all invalid: {', '.join(titles_found)}")

        # Check for removal of invalid titles
        if len(titles_found) > 1:  # Only consider removal if there are multiple titles
            for msg in track[:]:  # Iterate over a copy of the track
                if msg.type == 'track_name' and not is_valid_title(msg.name) and msg.name != new_name:
                    track.remove(msg)
                    changes_made = True  # Mark that a change was made
                    print(f"Removed invalid title from Track {i + 1}: {msg.name}")
        elif len(titles_found) == 1:
            # When there's only one title, do not remove it, regardless of validity
            if not valid_titles_found:
                print(f"Warning: Track {i + 1} has a single title that is invalid: {track[0].name}. Not removing it.")
                invalid_titles_found = True  # Mark that an invalid title was found but not removed

    # Adjust the condition to check for changes
    if not (track1_modified or changes_made):  # If no modifications were made
        print("No changes needed; the existing notes.mid is valid.")
        print()  # Blank echo statement
        return

    # Check if we need to rename the original file
    if track1_modified or invalid_titles_found or changes_made:
        # Rename old notes.mid to notes.mid.old or notes.mid.old1, notes.mid.old2, etc.
        base_old_file_path = file_path + '.old'
        old_file_path = base_old_file_path
        counter = 1
        
        if os.path.exists(old_file_path):
            print(f"'{old_file_path}' already exists. Incrementing the backup file name.")
        
        while os.path.exists(old_file_path):
            old_file_path = f"{base_old_file_path}{counter}"
            counter += 1
        
        os.rename(file_path, old_file_path)
        print(f"Renamed old MIDI file to: {old_file_path}")

        # Save the modified MIDI file as notes.mid
        midi.save(file_path)  # Save the modifications to notes.mid
        print(f"Modified MIDI file saved as: {file_path}")

    print()  # Blank echo statement

# Function to process a single notes.mid file and its song.ini file
def process_single_directory(directory):
    directory = directory.rstrip("\\/").strip('"')  # Strip trailing slashes/backslashes and quotes
    midi_file_path = os.path.join(directory, "notes.mid")
    ini_file_path = os.path.join(directory, "song.ini")

    if os.path.exists(midi_file_path) and os.path.exists(ini_file_path):
        song_name, artist = get_song_info(ini_file_path)
        if song_name and artist:
            modify_midi(midi_file_path, song_name, artist)
        else:
            print(f"Missing song name or artist in {ini_file_path}")
    else:
        print(f"Missing notes.mid or song.ini in {directory}")

# Function to process a list of directories
def process_multiple_directories(directories_file):
    with open(directories_file, 'r') as file:
        directories = [line.strip() for line in file.readlines()]

        for directory in directories:
            directory = directory.rstrip("\\/").strip('"')
            if os.path.isdir(directory):
                process_single_directory(directory)
            else:
                print(f"Directory does not exist: {directory}")

# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Modify MIDI files based on song.ini")
    
    parser.add_argument("--dir", type=str, help="Full path to the directory containing the notes.mid and song.ini")
    parser.add_argument("--list", type=str, help="Path to a file containing a list of directories to process")

    args = parser.parse_args()

    if args.dir:
        directory = args.dir.rstrip("\\/").strip('"')
        if os.path.isdir(directory):
            process_single_directory(directory)
        else:
            print(f"Directory does not exist: {directory}")
    
    if args.list:
        if os.path.isfile(args.list):
            process_multiple_directories(args.list)
        else:
            print(f"File does not exist: {args.list}")

# Run the script
if __name__ == "__main__":
    main()
