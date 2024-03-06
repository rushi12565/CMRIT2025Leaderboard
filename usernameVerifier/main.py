import csv
import os
import re
import requests
import sys
import logging
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from tqdm import tqdm

LEETCODE_QUERY = '''
https://leetcode.com/graphql?query=query
{     
      userContestRanking(username:  "{<username>}") 
      {
        attendedContestsCount
        rating
        globalRanking
        totalParticipants
        topPercentage    
      }
}
'''


class Participant:
    def __init__(self, handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle,
                 hackerrank_handle):
        self.handle = handle
        self.geeksforgeeks_handle = geeksforgeeks_handle
        self.codeforces_handle = codeforces_handle
        self.leetcode_handle = leetcode_handle
        self.codechef_handle = codechef_handle
        self.hackerrank_handle = hackerrank_handle


def remove_non_ascii(input_string):
    return re.sub(r'[\t\n\x0B\f\r]+', '', input_string)


def check_url_exists(url):
    # if url is leeetcode
    if "https://leetcode.com/" in url:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # read response as json
                response_json = response.json()
                # if the response contains the key "errors", then the handle does not exist
                if response_json.get("errors"):
                    return False, response.url
                return True, response.url
            return False, response.url
        except requests.exceptions.RequestException:
            return False, "Exception"
    header = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/121.0.0.0 Safari/537.36"
    }
    # if url is hackerrank
    if "https://www.hackerrank.com/" in url:
        try:
            response = requests.get(url, headers=header)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract the title of the page
            title = soup.title.string
            print(title)
            # Hackerrank handles that do not exist have the title "HTTP 404: Page Not Found | HackerRank"
            # But the title in beautiful soup is "Programming Problems and Competitions :: HackerRank"
            # If user exists, title will be " Name - User Profile | HackerRank"
            if "Programming Problems and Competitions :: HackerRank" in title:
                return False, response.url
            return True, response.url
        except requests.exceptions.RequestException:
            return False, "Exception"
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            # Check if the final URL is the same as the original URL (no redirect), if redirected, then URL does not
            # exist codeforces redirect is found by checking if final url is https://codeforces.com/ geeksforgeeks
            # redirect is found by checking if final url is
            # https://auth.geeksforgeeks.org/?to=https://auth.geeksforgeeks.org/profile.php codechef redirect is
            # found by checking if final url is https://www.codechef.com/ Hackerrank and Leetcode return 404 error if
            # handle does not exist
            if (response.url == "https://codeforces.com/" or response.url == ("https://auth.geeksforgeeks.org/?to=https"
                                                                              "://auth.geeksforgeeks.org/profile.php")
                    or response.url == "https://www.codechef.com/"):
                return False, response.url
            else:
                return True, response.url
        return False, response.url
    except requests.exceptions.RequestException:
        return False, "Exception"


def process_geeksforgeeks(participants):
    """
    Process GeeksForGeeks handles for each participant and log the progress.

    Args:
    participants (list): List of participant objects

    Returns:
    None
    """
    # Configure logging
    logging.basicConfig(filename='geeksforgeeks_debug.log', level=logging.DEBUG)

    # Iterate through each participant
    for participant in tqdm(participants, desc="Processing GeeksForGeeks Handles", unit="participant"):
        # Check if GeeksForGeeks handle is valid
        if participant.geeksforgeeks_handle != '#N/A':
            logging.debug(f"Checking GeeksForGeeks URL for participant {participant.handle}")

            # Check if the GeeksForGeeks URL exists
            geeksforgeeks_url_exists, response_url = check_url_exists(
                "https://auth.geeksforgeeks.org/user/" + participant.geeksforgeeks_handle)
            logging.debug(f"GeeksForGeeks URL exists: {geeksforgeeks_url_exists}, Response URL: {response_url}")

            # Retry if the GeeksForGeeks URL does not exist
            if not geeksforgeeks_url_exists and participant.geeksforgeeks_handle != '#N/A':
                logging.debug(f"Retrying GeeksForGeeks URL check for participant {participant.handle}")
                geeksforgeeks_url_exists, response_url = check_url_exists(
                    "https://auth.geeksforgeeks.org/user/" + participant.geeksforgeeks_handle)
                logging.debug(f"GeeksForGeeks URL retry: {geeksforgeeks_url_exists}, Response URL: {response_url}")

            # Write participant data to file
            with open('geeksforgeeks_handles.txt', 'a') as file:
                file.write(f"{participant.handle}, {participant.geeksforgeeks_handle}, {geeksforgeeks_url_exists}\n")
            logging.debug(
                f"Data written to file for participant {participant.handle}: {participant.geeksforgeeks_handle},"
                f" {geeksforgeeks_url_exists}")
            logging.debug("---------------------------------------------------")
    # Shutdown logging
    logging.shutdown()


def process_codeforces(participants):
    """
    Process Codeforces handles for each participant and log the progress.

    Args:
    participants (list): List of participant objects

    Returns:
    None
    """
    # Iterate through the list of participants and check if their Codeforces handle exists
    for participant in tqdm(participants, desc="Processing Codeforces Handles", unit="participant"):
        # Check if the Codeforces handle is not '#N/A'
        if participant.codeforces_handle != '#N/A':
            # Log the checking of Codeforces URL for the current participant
            logging.debug(f"Checking Codeforces URL for participant {participant.handle}")
            # Check if the URL exists and get the response URL
            codeforces_url_exists, response_url = check_url_exists("https://codeforces.com/profile/" + participant.codeforces_handle)

            # Log the result of the URL existence check
            logging.debug(f"Codeforces URL exists: {codeforces_url_exists}, Response URL: {response_url}")
            if not codeforces_url_exists and participant.codeforces_handle != '#N/A':
                # Log the retry of Codeforces URL check for the current participant
                logging.debug(f"Retrying Codeforces URL check for participant {participant.handle}")
                # Retry the URL existence check and get the response URL
                codeforces_url_exists, response_url = check_url_exists("https://codeforces.com/profile/" + participant.codeforces_handle)
                logging.debug(f"Codeforces URL retry: {codeforces_url_exists}, Response URL: {response_url}")

            # Write the participant's handle, Codeforces handle, and URL existence to a file
            with open('codeforces_handles.txt', 'a') as file:
                file.write(f"{participant.handle}, {participant.codeforces_handle}, {codeforces_url_exists}\n")

            # Log the data written to the file for the current participant
            logging.debug(f"Data written to file for participant {participant.handle}: {participant.codeforces_handle}, {codeforces_url_exists}")
            logging.debug("---------------------------------------------------")
    # Shutdown the logging system to release resources
    logging.shutdown()



def process_leetcode(participants):
    """
    Process LeetCode handles for participants and log the details.

    Args:
    participants (list): List of participant objects

    Returns:
    None
    """
    # Configure logging
    logging.basicConfig(filename='leetcode_debug.log', level=logging.DEBUG)

    # Iterate through participants and process LeetCode handles
    for participant in tqdm(participants, desc="Processing LeetCode Handles", unit="participant"):
        # Log LeetCode URL checking
        logging.debug(f"Checking LeetCode URL for participant {participant.handle}")

        # Check if participant has a valid LeetCode handle
        if participant.leetcode_handle != '#N/A':
            # Construct LeetCode query URL
            url = LEETCODE_QUERY.replace("{<username>}", participant.leetcode_handle)
            url = url.replace(" ", "%20")
            logging.debug(f"LeetCode URL: \n{url}")

            # Check if the LeetCode URL exists
            leetcode_url_exists, response_url = check_url_exists(url)
            logging.debug(f"LeetCode URL exists: {leetcode_url_exists}, Response URL: {response_url}")

            # Retry checking LeetCode URL if it doesn't exist
            if not leetcode_url_exists and participant.leetcode_handle != '#N/A':
                logging.debug(f"Retrying LeetCode URL check for participant {participant.handle}")
                leetcode_url_exists, response_url = check_url_exists(url)
                logging.debug(f"LeetCode URL retry: {leetcode_url_exists}, Response URL: {response_url}")

            # Write participant data to file
            with open('leetcode_handles.txt', 'a') as file:
                file.write(f"{participant.handle}, {participant.leetcode_handle}, {leetcode_url_exists}\n")
            logging.debug(f"Data written to file for participant {participant.handle}: {participant.leetcode_handle},"
                          f" {leetcode_url_exists}")
            logging.debug("---------------------------------------------------")

    # Shutdown logging
    logging.shutdown()


def process_codechef(participants):
    """
    Process the CodeChef handles for the given participants and log the progress.

    Args:
    participants (list): List of Participant objects.

    Returns:
    None
    """
    logging.basicConfig(filename='codechef_debug.log', level=logging.DEBUG)
    for participant in tqdm(participants, desc="Processing CodeChef Handles", unit="participant"):
        # Check CodeChef URL for each participant
        logging.debug(f"Checking CodeChef URL for participant {participant.handle}")

        if participant.codechef_handle != '#N/A':
            # Check if CodeChef URL exists
            codechef_url_exists, response_url = check_url_exists(
                "https://www.codechef.com/users/" + participant.codechef_handle)
            logging.debug(f"CodeChef URL exists: {codechef_url_exists}, Response URL: {response_url}")

            if not codechef_url_exists and participant.codechef_handle != '#N/A':
                # Retry checking CodeChef URL
                logging.debug(f"Retrying CodeChef URL check for participant {participant.handle}")
                codechef_url_exists, response_url = check_url_exists(
                    "https://www.codechef.com/users/" + participant.codechef_handle)
                logging.debug(f"CodeChef URL retry: {codechef_url_exists}, Response URL: {response_url}")

            # Write participant data to file
            with open('codechef_handles.txt', 'a') as file:
                file.write(f"{participant.handle}, {participant.codechef_handle}, {codechef_url_exists}\n")
            logging.debug(f"Data written to file for participant {participant.handle}: {participant.codechef_handle},"
                          f" {codechef_url_exists}")
            logging.debug("---------------------------------------------------")

    logging.shutdown()


def process_hackerrank(participants):
    """
    Process the HackerRank handles for the given participants and log the debugging information.

    Args:
    participants (list): List of Participant objects

    Returns:
    None
    """
    # Configure logging
    logging.basicConfig(filename='hackerrank_debug.log', level=logging.DEBUG)

    # Iterate through the participants
    for participant in tqdm(participants, desc="Processing HackerRank Handles", unit="participant"):
        # Log the participant's HackerRank URL check
        logging.debug(f"Checking HackerRank URL for participant {participant.handle}")

        # Check if the HackerRank URL exists
        if participant.hackerrank_handle != '#N/A':
            hackerrank_url_exists, response_url = check_url_exists(
                "https://www.hackerrank.com/profile/" + participant.hackerrank_handle)
            logging.debug(f"HackerRank URL exists: {hackerrank_url_exists}, Response URL: {response_url}")

            # Retry the HackerRank URL check if it doesn't exist
            if not hackerrank_url_exists and participant.hackerrank_handle != '#N/A':
                logging.debug(f"Retrying HackerRank URL check for participant {participant.handle}")
                hackerrank_url_exists, response_url = check_url_exists(
                    "https://www.hackerrank.com/profile/" + participant.hackerrank_handle)
                logging.debug(f"HackerRank URL retry: {hackerrank_url_exists}, Response URL: {response_url}")

            # Write data to file
            with open('hackerrank_handles.txt', 'a') as file:
                file.write(f"{participant.handle}, {participant.hackerrank_handle}, {hackerrank_url_exists}\n")
            logging.debug(f"Data written to file for participant {participant.handle}: {participant.hackerrank_handle},"
                          f" {hackerrank_url_exists}")
            logging.debug("---------------------------------------------------")

    # Shutdown logging
    logging.shutdown()


def load_excel_sheet(excel_sheet_path):
    participants = []
    workbook = load_workbook(excel_sheet_path)
    sheet = workbook.active
    total_rows = sheet.max_row - 2
    count = 1
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if all(x == 'None' for x in row):
            break
        handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle, hackerrank_handle = row
        print(f"( {count} / {total_rows} ) Loading participant {handle}")
        participants.append(
            Participant(handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle,
                        hackerrank_handle))
        count += 1
    print("Finished loading participants")
    return participants


def load_csv_sheet(csv_sheet_path):
    """
    Load participant data from a CSV sheet and return a list of Participant objects.

    Args:
    csv_sheet_path (str): The file path to the CSV sheet

    Returns:
    list: A list of Participant objects
    """
    participants = []
    with open(csv_sheet_path, 'r') as temp_file:
        temp_reader = csv.reader(temp_file)  # Create a temporary reader to count total rows
        total_rows = sum(1 for _ in temp_reader) - 2  # Calculate total rows in the CSV
        # close the temporary file
        temp_file.close()
    with open(csv_sheet_path, 'r') as file:
        reader = csv.reader(file)
        print(f"Total rows in CSV: {total_rows}")  # Print the total rows in the CSV
        count = 1
        for row in reader:
            if row[0] == "Admn No:":  # Skip the header row
                continue
            if all(x == 'None' or x == '' for x in row):  # Stop if all cells in the row are empty
                break
            handle, name = row[:2]
            geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle, hackerrank_handle = row[2:7]
            print(f"( {count} / {total_rows} ) Loading participant {handle}")  # Print progress
            participant = Participant(handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle,
                                      hackerrank_handle)  # Create Participant object
            participants.append(participant)  # Add Participant object to list
            count += 1
    print("Finished loading participants")
    file.close()
    return participants


def combine_results():
    """
    Combines handle details from multiple files and writes them to a CSV file called participant_details.csv.
    Each file contains handle details for a different platform, and the function loops through each file,
    reads the handle details, and writes them to the CSV file.
    """

    # Open participant_details.csv for writing
    with open('participant_details.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write header row to CSV
        writer.writerow(['Handle', 'GeeksForGeeks Handle', 'Codeforces Handle', 'LeetCode Handle', 'CodeChef Handle',
                         'HackerRank Handle', 'GeeksForGeeks URL Exists', 'Codeforces URL Exists',
                         'LeetCode URL Exists',
                         'CodeChef URL Exists', 'HackerRank URL Exists'])

        # Loop through each file and write handle details to CSV
        for file_name in ['geeksforgeeks_handles.txt', 'codeforces_handles.txt', 'leetcode_handles.txt',
                          'codechef_handles.txt', 'hackerrank_handles.txt']:
            with open(file_name, 'r') as file:
                for line in file:
                    data = line.strip().split(', ')
                    writer.writerow(data)
                    print(f'Writing data: {data}')
            print(f'Finished writing data from {file_name}')
            print('-----------------------------------------')
        print('Finished writing all data to participant_details.csv')


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <excel/csv file path> <platform>")
        return

    file_path = sys.argv[1]
    platform = sys.argv[2].lower()

    platforms = ['geeksforgeeks', 'codeforces', 'leetcode', 'codechef', 'hackerrank']

    if platform not in platforms and platform != 'all' and platform != 'combine':
        print("Invalid platform. Please choose one of: GeeksForGeeks, Codeforces, LeetCode, CodeChef, HackerRank, "
              "All, Combine")
        return

    if not os.path.isfile(file_path):
        print("File does not exist.")
        return

    if file_path.endswith('.xlsx'):
        participants = load_excel_sheet(file_path)
    elif file_path.endswith('.csv'):
        participants = load_csv_sheet(file_path)
    else:
        print("Invalid file format. Please provide an Excel (.xlsx) or CSV (.csv) file.")
        return

    if platform == 'geeksforgeeks' or platform == 'all':
        process_geeksforgeeks(participants)
    if platform == 'codeforces' or platform == 'all':
        process_codeforces(participants)
    if platform == 'leetcode' or platform == 'all':
        process_leetcode(participants)
    if platform == 'codechef' or platform == 'all':
        process_codechef(participants)
    if platform == 'hackerrank' or platform == 'all':
        process_hackerrank(participants)
    if platform == 'combine':
        combine_results()


if __name__ == "__main__":
    main()
