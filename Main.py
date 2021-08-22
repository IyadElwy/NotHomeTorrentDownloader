import os

import ezgmail, selenium.webdriver


class UserInfo:
    """A class containing the users info needed for running the program"""

    def __init__(self, utorrent_web_path: str, email_address: str, credentials_file_path: str):
        self.utorrent_web_path = utorrent_web_path
        self.email_address = email_address
        self.credentials_file_path = credentials_file_path


class FirstTime:
    """A class that sets up the users first time using the program"""

    def __init__(self):
        print("Hello and welcome to the Remote Torrent downloader for Windows.\nAt the moment the only"
              "torrent client supported is uTorrent web, the only websites: [Yts.mx, Rarbg.org]\n"
              "and the only email provider [Gmail].\n"
              "Please follow the instructions carefully to assure a successful setup.\n\n")
        print("1- Enable the Gmail API\n"
              "2- Download the credentials.json file\n"
              "3- Add your email as a tester in the developer settings\n"
              "4- Follow the pop up page which will open in your browser\n\n")
        user_info = UserInfo(input("Please enter the path to your utorrent web exe file: "),
                             input("Please enter your email address: "),
                             input("Please enter the path to your credentials.json file: "))
        os.system("pip install requirements.txt")
        os.system(f"copy {user_info.credentials_file_path} {os.getcwd()}")


class Checker:
    """A class that deals with checking the inbox for any download requests you make"""

    def __init__(self):
        pass


if __name__ == '__main__':
    pass

# TODO: IO for validating if it's the users first time or not

# TODO: pass the credentials.json and token.json file paths to program.
# TODO: program then creates copy of the files in working directory of program
# TODO: if its first time then print a small guide and ask for info needed

# TODO:
