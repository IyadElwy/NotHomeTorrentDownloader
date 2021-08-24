import os
import time
import pyinputplus
import ezgmail, selenium.webdriver
import pickle
from inputimeout import inputimeout, TimeoutOccurred
import traceback
from threading import Timer


class UserInfo:
    """A class containing the users info needed for running the program"""

    def __init__(self, utorrent_web_path: str, email_address: str, credentials_file_path: str,
                 first_time: bool = False):
        self.first_time = first_time
        self.utorrent_web_path = utorrent_web_path
        self.email_address = email_address
        self.credentials_file_path = credentials_file_path


class FirstTime:
    """A class that sets up the users first time using the program"""

    def __init__(self):
        print("\n\nHello and welcome to the Remote Torrent downloader for Windows.\nAt the moment the only "
              "torrent client supported is uTorrent web, the only websites: [Yts.mx, Rarbg.org]\n"
              "and the only email provider [Gmail].\n"
              "Please follow the instructions carefully to assure a successful setup.\n\n")
        print("1- Enable the Gmail API\n"
              "2- Download the credentials.json file\n"
              "3- Add your email as a tester in the developer settings\n"
              "4- Follow the pop up page which will open in your browser\n"
              "You will be redirected to the pop up page shortly...\n\n")
        time.sleep(5)
        ezgmail.init()
        self.user_info = UserInfo(pyinputplus.inputFilepath("Please enter the path to your utorrent web .exe file: "),
                                  pyinputplus.inputEmail("Please enter your email address: "),
                                  pyinputplus.inputFilepath("Please enter the path to your credentials.json file: "))
        with open("user_info_file", "wb") as user_info_file:
            pickle.dump(self.user_info, user_info_file)
        os.system("pip install requirements.txt")
        os.system(f"copy {self.user_info.credentials_file_path} {os.getcwd()}")


class Checker:
    """A class that deals with checking the inbox for any download requests you make"""

    def __init__(self, intervals: int):
        self.keep_running_checks = True
        while self.keep_running_checks:
            timer = Timer(intervals, self.check_continue)
            timer.start()
            should_exit = input("\nEnter 'E' to exit program: \n\n")
            if should_exit == "E":
                self.keep_running_checks = False
            else:
                self.keep_running_checks = True
                timer.cancel()

        print("\nSession terminated.\n")

    @staticmethod
    def check_continue():
        unread_threads = ezgmail.unread()
        for i in range(3):
            print(unread_threads[i].text)
            print("----")


if __name__ == '__main__':
    commands = {
        "download torrent rarbg": 1,
        "download torrent yts": 2,
        "check download status": 3,
        "shut down pc": 4,
        "shut down pc after finished": 5,
        "do command": 6
    }

    try:
        with open("user_info_file", "rb") as user_info_file:
            user_info = pickle.load(user_info_file)
            if user_info.first_time:
                first_time = FirstTime()
                ezgmail.send(first_time.user_info.email_address, 'Confirmation Of Setup',
                             'This email confirms the successful setup of the Not_Home_Torrent_Downloader')
                print("An email was sent to you for confirmation of a successful setup.")
            else:
                print("\n\nHello and welcome to the Remote Torrent downloader for Windows.\n\n")
                intervals_for_checking = pyinputplus.inputInt(
                    "Please enter the intervals you wish the program to check for requests [minutes] : ")
                Checker(intervals_for_checking)
    except:
        print("\n\nAn error occurred: ")
        traceback.print_exc()

# TODO: Add requirements.txt at end
# TODO: Add feature to give option of turning pc off after all downloads have finished
# TODO: Add feature of being able to type any commands through email and have the program execute them
# TODO: Use keywords and a guide for the usage for sending mails so how to initiate certain commands of the program
# TODO: always get reply after sending a command if it is successful or not and what kind of info they requested or
#  what their command did
# TODO: commands: turn pc off after all downloads finish, type any cmd commands, get summary of all download statuses
# TODO: Have user chooose the interval of email checks the program should do
# TODO: remove test input time
