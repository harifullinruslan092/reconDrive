import os
import shutil
from datetime import datetime, timedelta
import time
import re
import xml.etree.ElementTree as ET
import traceback

# Global variables
filesRecon = []
filesOneDrive = []
copiedFiles = set()


def ReconToOneDrive(dirPathRecon, dirPathOneDrive, interval):
    print("Program started!")
    print("Press Ctrl+C to stop the program")
    while True:
        try:
            # get all files from Recon folder
            for path, subdirs, files in os.walk(dirPathRecon):
                for file in files:
                    filesRecon.append(os.path.join(
                        path, file).replace(dirPathRecon, ""))

            # get all files from OneDrive folder
            for path, subdirs, files in os.walk(dirPathOneDrive):
                for file in files:
                    filesOneDrive.append(os.path.join(
                        path, file).replace(dirPathOneDrive, ""))

            # copy files from Recon to OneDrive
            for file in filesRecon:
                if file in filesOneDrive or file in copiedFiles:
                    continue
                else:
                    if file:
                        # Find the last occurrence of '\'
                        last_backslash_index = file.rfind('\\')

                        # Extract substring from the last '\'
                        substring = file[last_backslash_index + 1:]

                        # Check for and replace specific symbols in the substring
                        substring = re.sub(r'[^a-zA-Z0-9.]', '', substring)

                        # Join the modified substring to the end of the original string
                        new_file = file[:last_backslash_index + 1] + substring

                        os.makedirs(os.path.dirname(
                            dirPathOneDrive + new_file), exist_ok=True)
                        shutil.copy(dirPathRecon + file,
                                    dirPathOneDrive + new_file)
                        copiedFiles.add(file)
                        print(
                            f"Added: {new_file} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            filesRecon.clear()
            filesOneDrive.clear()
        except Exception as e:
            log_error(e)
            print("Error occurred, check errors.txt for details")
        time.sleep(interval)


def removeOldFiles(dirPathOneDrive, interval, remove_term):
    try:
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=remove_term * 30)

        # Iterate over files in dirPathOneDrive
        for root, dirs, files in os.walk(dirPathOneDrive):
            for file in files:
                file_path = os.path.join(root, file)

                # Get the last modification time of the file
                file_mtime = os.path.getmtime(file_path)

                # Convert the modification time to a datetime object
                file_mtime_dt = datetime.fromtimestamp(file_mtime)

                # Check if the file is older than the cutoff date
                if file_mtime_dt < cutoff_date:
                    os.remove(file_path)
                    print(
                        f"Removed old file: {file_path} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        # Add a sleep interval to avoid continuous execution
        time.sleep(interval)
    except Exception as e:
        log_error(f"Error removing old files: {e}")


def parse_settings():
    settings = {}
    try:
        # choose file with program setting
        tree = ET.parse('settings.xml')
        root = tree.getroot()
        settings['dirPathRecon'] = root.find('path-recon').text.strip()
        settings['dirPathOneDrive'] = root.find('path-one-drive').text.strip()
        settings['interval'] = int(root.find('interval').text)
        settings['remove_term'] = int(root.find('auto-remove-term').text)
    except Exception as e:
        log_error(f"Error parsing settings: {e}")
    return settings


def log_error(exception):
    with open('errors.txt', 'a') as error_file:
        error_file.write(f"Error: {exception}\n")
        error_file.write(f"Traceback: {traceback.format_exc()}\n")


if __name__ == "__main__":
    settings = parse_settings()
    dirPathRecon = settings['dirPathRecon']
    dirPathOneDrive = settings['dirPathOneDrive']
    interval = settings['interval']
    remove_term = settings['remove_term']
    try:
        ReconToOneDrive(dirPathRecon, dirPathOneDrive, interval)
        removeOldFiles(dirPathOneDrive, interval, remove_term)
    except KeyboardInterrupt:
        print("Program stopped by user")
    except Exception as e:
        log_error(e)
        print("Unexpected error occurred, check errors.txt for details")
