import openpyxl
import requests
import csv
import re
from bs4 import BeautifulSoup
from tqdm import tqdm  # Import tqdm library for progress bar

"""
Removes non-ASCII characters from the input_string.

Args:
    input_string (str): The input string containing non-ASCII characters.
    
Returns:
    str: The input string with non-ASCII characters removed.
"""
def remove_non_ascii(input_string):
    return re.sub(r'[\t\n\x0B\f\r]+', '', input_string)

"""
Class to store participant details.

Attributes:
    handle (str): The participant's handle.
    geeksforgeeks_handle (str): The participant's GeeksForGeeks handle.
    codeforces_handle (str): The participant's Codeforces handle.
    leetcode_handle (str): The participant's LeetCode handle.
    codechef_handle (str): The participant's CodeChef handle.
    hackerrank_handle (str): The participant's HackerRank handle.

Methods:
    __init__(handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle, hackerrank_handle):
        Initializes a Participant object with the given handles.
"""
class Participant:
    # Class to store participant details
    def __init__(self, handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle,
                 hackerrank_handle):
        # type cast all handles to string
        handle = str(handle)
        geeksforgeeks_handle = str(geeksforgeeks_handle)
        codeforces_handle = str(codeforces_handle)
        leetcode_handle = str(leetcode_handle)
        codechef_handle = str(codechef_handle)
        hackerrank_handle = str(hackerrank_handle)

        self.handle = handle
        self.codeforces_handle = codeforces_handle
        self.geeksforgeeks_handle = geeksforgeeks_handle
        self.leetcode_handle = leetcode_handle
        self.codechef_handle = codechef_handle
        if hackerrank_handle.startswith('@'):
            hackerrank_handle = hackerrank_handle[1:]
        self.hackerrank_handle = hackerrank_handle


"""
Function to load the excel sheet and return a list of Participant objects.

Parameters:
- excel_sheet_path (str): The path to the excel sheet.

Returns:
- participants (list): A list of Participant objects.

Description:
This function takes the path to an excel sheet as input and loads the sheet using the openpyxl library. It then iterates over the rows of the sheet, starting from the second row, and creates a Participant object for each row. The Participant object is initialized with the values from the row, including the handle, GeeksForGeeks handle, Codeforces handle, LeetCode handle, CodeChef handle, and HackerRank handle. The Participant object is then added to the list of participants.

The function uses the tqdm library to display a progress bar while processing the participants.

Example:
excel_sheet_path = "path/to/excel/sheet.xlsx"
participants = load_excel_sheet(excel_sheet_path)
"""
def load_excel_sheet(excel_sheet_path):
    # Function to load the excel sheet and return a list of Participant objects
    participants = []

    workbook = openpyxl.load_workbook(excel_sheet_path)
    sheet = workbook.active

    for row in tqdm(sheet.iter_rows(min_row=2, values_only=True), desc="Processing Participants", unit="participant"):
        # replace spaces with empty string
        row = [str(x).strip() for x in row]
        # if all elements of the row are 'None', then break
        if all(x == 'None' for x in row):
            break
        handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle, hackerrank_handle = row
        participants.append(
            Participant(handle,geeksforgeeks_handle,  codeforces_handle, leetcode_handle, codechef_handle,
                        hackerrank_handle))

    return participants

def load_csv_sheet(csv_sheet_path):
    # Function to load the csv sheet and return a list of Participant objects
    participants = []

    with open(csv_sheet_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # skip the first row
            if row[0] == "Admn No:":
                continue
            # stop reading if all elements of the row are 'None' or empty
            if all(x == 'None' or x == '' for x in row):
                break
            # Admn No:,Name,GFG,CODEFORCES,LEETCODE,CODECHEF,HACKERRANK
            handle, name, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle, hackerrank_handle = row
            participants.append(
                Participant(handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle,
                            hackerrank_handle))

    return participants


"""
Check if a given URL exists.

Parameters:
- url (str): The URL to check.

Returns:
- tuple: A tuple containing a boolean value indicating whether the URL exists or not, and the final URL after any redirects.

Example:
>>> check_url_exists("https://leetcode.com/")
(True, "https://leetcode.com/")

>>> check_url_exists("https://www.hackerrank.com/")
(True, "https://www.hackerrank.com/")

>>> check_url_exists("https://www.google.com/")
(True, "https://www.google.com/")

>>> check_url_exists("https://www.example.com/")
(False, "https://www.example.com/")

>>> check_url_exists("https://www.nonexistenturl.com/")
(False, "https://www.nonexistenturl.com/")
"""
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
       "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
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
            if response.url == "https://codeforces.com/" or response.url == "https://auth.geeksforgeeks.org/?to=https://auth.geeksforgeeks.org/profile.php" or response.url == "https://www.codechef.com/":
                return False, response.url
            else:
                return True, response.url
        return False, response.url
    except requests.exceptions.RequestException:
        return False, "Exception"


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


def main():
    csv_sheet_path = "..//src//main//resources//CMRIT2025Leaderboard.csv"
    participants = load_csv_sheet(csv_sheet_path)
    # if log.txt exists, delete it
    try:
        open('log.txt', 'r')
        open('log.txt', 'w').close()
    except FileNotFoundError:
        pass

    # check if participant_details.csv exists, delete it
    try:
        open('..//src//main//resources//participant_details.csv', 'r')
        open('..//src//main//resources//participant_details.csv', 'w').close()
    except FileNotFoundError:
        pass

    # If folder does not exist, create it
    try:
        open('..//src//main//resources//participant_details.csv', 'r')
    except FileNotFoundError:
        open('..//src//main//resources//participant_details.csv', 'w').close()

    with open('..//src//main//resources//participant_details.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Handle', 'GeeksForGeeks Handle', 'Codeforces Handle', 'LeetCode Handle', 'CodeChef Handle',
                         'HackerRank Handle', 'GeeksForGeeks URL Exists', 'Codeforces URL Exists',
                         'LeetCode URL Exists',
                         'CodeChef URL Exists', 'HackerRank URL Exists'])

        log_writer = open('log.txt', 'a')

        for participant in tqdm(participants, desc="Checking URLs", unit="participant"):
            handle = participant.handle
            geeksforgeeks_handle = participant.geeksforgeeks_handle
            codeforces_handle = participant.codeforces_handle
            leetcode_handle = participant.leetcode_handle
            codechef_handle = participant.codechef_handle
            hackerrank_handle = participant.hackerrank_handle

            # Remove all special characters
            handle = remove_non_ascii(handle)
            geeksforgeeks_handle = remove_non_ascii(geeksforgeeks_handle)
            codeforces_handle = remove_non_ascii(codeforces_handle)
            leetcode_handle = remove_non_ascii(leetcode_handle)
            codechef_handle = remove_non_ascii(codechef_handle)
            hackerrank_handle = remove_non_ascii(hackerrank_handle)


            row = [handle, geeksforgeeks_handle, codeforces_handle, leetcode_handle, codechef_handle, hackerrank_handle]

            # Check if GeeksForGeeks URL exists
            if geeksforgeeks_handle != '#N/A':
                geeksforgeeks_url_exists, response_url = check_url_exists(
                    "https://auth.geeksforgeeks.org/user/" + geeksforgeeks_handle)
            else:
                geeksforgeeks_url_exists = False
                response_url = "N/A"

            if not geeksforgeeks_url_exists and geeksforgeeks_handle != '#N/A':
                # Retry once
                geeksforgeeks_url_exists, response_url = check_url_exists(
                    "https://auth.geeksforgeeks.org/user/" + geeksforgeeks_handle)

            # Write to log.txt, all details of participant
            log_writer.write(
                f"GeeksForGeeks Handle: {geeksforgeeks_handle}\nGeeksForGeeks URL: https://auth.geeksforgeeks.org/user/{geeksforgeeks_handle}\nResponse URL: {response_url}\nGeeksForGeeks URL Exists: {geeksforgeeks_url_exists}\n\n")

            # Checking if Codeforces URL exists
            if codeforces_handle != '#N/A':
                codeforces_url_exists, response_url = check_url_exists(
                    "https://codeforces.com/profile/" + codeforces_handle)
            else:
                codeforces_url_exists = False
                response_url = "N/A"

            if not codeforces_url_exists and codeforces_handle != '#N/A':
                # Retry once
                codeforces_url_exists, response_url = check_url_exists(
                    "https://codeforces.com/profile/" + codeforces_handle)

            # Write to log.txt, all details of participant for codeforces
            log_writer.write(
                f"Handle: {handle}\nCodeforces Handle: {codeforces_handle}\nCodeforces URL: https://codeforces.com/profile/{codeforces_handle}\nResponse URL: {response_url}\nCodeforces URL Exists: {codeforces_url_exists}\n\n")

            # Checking if LeetCode URL exists
            if leetcode_handle != '#N/A':
                url = LEETCODE_QUERY.replace("{<username>}", leetcode_handle)
                # encode the url
                url = url.replace(" ", "%20")
                leetcode_url_exists, response_url = check_url_exists(url)
            else:
                leetcode_url_exists = False
                response_url = "N/A"

            if not leetcode_url_exists and leetcode_handle != '#N/A':
                # Retry once
                leetcode_url_exists, response_url = check_url_exists(url)

            # Write to log.txt, all details of participant for LeetCode
            log_writer.write(
                f"LeetCode Handle: {leetcode_handle}\nLeetCode URL: https://leetcode.com/{leetcode_handle}\nResponse URL: {response_url}\nLeetCode URL Exists: {leetcode_url_exists}\n\n")

            # Checking if CodeChef URL exists
            if codechef_handle != '#N/A':
                codechef_url_exists, response_url = check_url_exists(
                    "https://www.codechef.com/users/" + codechef_handle)
            else:
                codechef_url_exists = False
                response_url = "N/A"

            if not codechef_url_exists and codechef_handle != '#N/A':
                # Retry once
                codechef_url_exists, response_url = check_url_exists(
                    "https://www.codechef.com/users/" + codechef_handle)

            # Write to log.txt, all details of participant for CodeChef
            log_writer.write(
                f"CodeChef Handle: {codechef_handle}\nCodeChef URL: https://www.codechef.com/users/{codechef_handle}\nResponse URL: {response_url}\nCodeChef URL Exists: {codechef_url_exists}\n\n")

            # Checking if HackerRank URL exists
            if hackerrank_handle != '#N/A':
                hackerrank_url_exists, response_url = check_url_exists(
                    "https://www.hackerrank.com/profile/" + hackerrank_handle)
            else:
                hackerrank_url_exists = False
                response_url = "N/A"

            if not hackerrank_url_exists and hackerrank_handle != '#N/A':
                # Retry once
                hackerrank_url_exists, response_url = check_url_exists(
                    "https://www.hackerrank.com/profile/" + hackerrank_handle)

            # Write to log.txt, all details of participant for HackerRank
            log_writer.write(
                f"HackerRank Handle: {hackerrank_handle}\nHackerRank URL: https://www.hackerrank.com/profile/{hackerrank_handle}\nResponse URL: {response_url}\nHackerRank URL Exists: {hackerrank_url_exists}\n\n")

            row.extend([geeksforgeeks_url_exists, codeforces_url_exists, leetcode_url_exists, codechef_url_exists,
                        hackerrank_url_exists])

            log_writer.write(
                "================================================================================================================================================================================\n")

            writer.writerow(row)


if __name__ == "__main__":
    main()
