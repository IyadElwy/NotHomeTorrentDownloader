import os
import time
import pyinputplus
import ezgmail
from selenium import webdriver
import pickle
import traceback
from inputimeout import inputimeout, TimeoutOccurred
import subprocess


class UserInfo:
    """A class containing the users info needed for running the program"""

    def __init__(self, utorrent_web_path: str, email_address: str, credentials_file_path: str, chrome_path: str,
                 first_time: bool = False):
        self.first_time = first_time
        self.utorrent_web_path = utorrent_web_path
        self.email_address = email_address
        self.credentials_file_path = credentials_file_path
        self.chrome_path = chrome_path


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
                                  pyinputplus.inputFilepath("Please enter the path to your credentials.json file: "),
                                  pyinputplus.inputFilepath("Please enter to your chrome.exe file: "))
        with open("user_info_file", "wb") as user_info_file:
            pickle.dump(self.user_info, user_info_file)
        os.system("pip install requirements.txt")
        os.system(f"copy {self.user_info.credentials_file_path} {os.getcwd()}")


class Checker:
    """A class that deals with checking the inbox for any download requests you make"""

    def __init__(self, intervals: int, user_info: UserInfo):
        self.keep_running_checks = True
        self.initiate_checking(intervals)

    def check_for_keyword(self, unread_threads: ezgmail.unread) -> tuple:
        commands = {
            "download torrent rarbg": 1,
            "download torrent yts": 2,
            "check download status": 3,
            "shut down pc": 4,
            "shut down pc after finished": 5,
            "do command": 6,
            "help": 7
        }
        lim = 0 if len(unread_threads) <= 0 else 1 if len(unread_threads) == 1 else 2 if len(unread_threads) == 2 else 3

        for i in range(lim):
            unread_thread = unread_threads[i].text[0]
            for command in commands:
                if command in unread_thread:
                    unread_threads[i].markAsRead()
                    return commands.get(command), unread_thread
        return 0, ""

    def initiate_checking(self, intervals: int):
        shut_down_after_done = False
        if self.keep_running_checks:
            unread_threads = ezgmail.unread()
            command, message = self.check_for_keyword(unread_threads)
            if command == 1:
                DownloadRarbgTorrent(message, user_info)
            elif command == 2:
                DownloadYtsTorrent(message, user_info)
            elif command == 3:
                CheckDownloadStatus(user_info)
            elif command == 4:
                ShutDownPc(user_info)
            elif command == 5:
                shut_down_after_done = ShutDownPc(user_info, True)
            elif command == 6:
                DoCommand(message, user_info)
            elif command == 7:
                ShowHelp(user_info)

            try:
                should_exit = inputimeout(prompt="\nEnter 'E' to exit program:", timeout=intervals * 60)
                if should_exit == "E":
                    self.keep_running_checks = False
                    print("\nSession terminated.\n")
                else:
                    self.initiate_checking(intervals)

            except TimeoutOccurred:
                self.initiate_checking(intervals)
                if shut_down_after_done.should_shutdown_after_done:
                    ShutDownPc(user_info, True)


class ShowHelp:
    def __init__(self, user_info: UserInfo):
        commands = "download torrent rarbg\ndownload torrent yts\ncheck download status\nshut down pc\nshut down pc " \
                   "after " \
                   "finished\ndo command\nhelp\n"

        ezgmail.send(user_info.email_address, "Help Reply", f"The commands are : \n{commands}")


class DownloadRarbgTorrent:
    def __init__(self, message: str, user_info: UserInfo):
        # TODO: implement text from image recognition
        link = reformat_msg(message)
        try:
            browser = webdriver.Chrome()
            browser.get(link)
            time.sleep(10)
            magnet_link = browser.find_element_by_css_selector(
                """body > table:nth-child(7) > tbody > tr > td:nth-child(2) > div > table > tbody > tr:nth-child(2) > 
                td > div > table > tbody > tr:nth-child(1) > td.lista > a:nth-child(3)""")
            print(magnet_link.text)


        except:
            print("Error getting page")


class DownloadYtsTorrent:
    def __init__(self, message: str, user_info: UserInfo):
        link = reformat_msg(message)
        try:
            browser = webdriver.Chrome()
            browser.get(link)
            time.sleep(3)
            download_btn = browser.find_element_by_css_selector(
                """#movie-poster > a""")
            download_btn.click()
            time.sleep(3)
            magnet_link_element = browser.find_element_by_css_selector(
                """#movie-content > div:nth-child(1) > div.modal.modal-download.hidden-xs.hidden-sm.modal-active > 
                div > div.modal-content > div:nth-child(1) > a.magnet-download.download-torrent.magnet""")

            magnet_link = magnet_link_element.get_attribute("href")
            time.sleep(3)
            add_torrent(magnet_link)
            ezgmail.send(user_info.email_address, "Movie Successfully added", f"The movie with the link:\n{link}\n"
                                                                              f"has been successfully added from "
                                                                              f"yts.mx")
        except:
            print("Error getting page")


class CheckDownloadStatus:
    def __init__(self, user_info: UserInfo, send_mail=True):
        self.status_list = check_utorrent_web(user_info)
        status_msg = "\n".join(self.status_list)
        if send_mail:
            ezgmail.send(user_info.email_address, "Status of torrents", status_msg)

    def check_if_all_finished(self):
        for torrent in self.status_list:
            if "Downloading" in torrent:
                return False
            else:
                return True
        return False


class ShutDownPc:
    def __init__(self, user_info: UserInfo, after_finished: bool = False):
        self.should_shutdown_after_done = after_finished
        try:
            if after_finished:
                status = CheckDownloadStatus(user_info, False)
                if status.check_if_all_finished():
                    ezgmail.send(user_info.email_address, "Command successfully executed.", "Pc shut down after all "
                                                                                            "downloads have finished.")
                    subprocess.run("shutdown /s")

            else:
                ezgmail.send(user_info.email_address, "Command successfully executed.", "Pc shut down")
                subprocess.run("shutdown /s")

        except:
            ezgmail.send(user_info.email_address, "Command Error", f"Pc did not shut down.")


class DoCommand:
    def __init__(self, message: str, user_info: UserInfo):
        reformatted_msg = reformat_msg(message)
        try:
            subprocess.run(reformatted_msg)
            ezgmail.send(user_info.email_address, "Command successfully executed.", f"The command: '"
                                                                                    f"{reformatted_msg}' has been "
                                                                                    f"successfully executed.")
        except:
            ezgmail.send(user_info.email_address, "Command Error", f"The command: '"
                                                                   f"{reformatted_msg}' caused an "
                                                                   f"error.")


def reformat_msg(message: str) -> str:
    list_without_raw = [lin.rstrip("\r") for lin in message.split("\n")[1:-1]]
    vital_message_part = " ".join(list_without_raw)
    return vital_message_part


def check_utorrent_web(user_info: UserInfo) -> list[str]:
    browser = webdriver.Chrome()
    while True:
        try:
            browser.get(
                "https://utweb.trontv.com/gui/index.html?v=1.2.1.3583&localauth=localapibf2ae50bd9195d86:#/library")
            time.sleep(10)
            finished_torrents_names = browser.find_elements_by_class_name("""media-element-title""")
            finished_torrents_status = browser.find_elements_by_class_name("""auto-status""")
            torrent_with_status = list()

            for index, element in enumerate(finished_torrents_names):
                torrent_with_status.append(str(element.text + ": " + finished_torrents_status[index].text))

            return torrent_with_status
        except:
            browser.refresh()


def add_torrent(magnet_url: str):
    browser = webdriver.Chrome()
    while True:
        try:
            browser.get(
                "https://utweb.trontv.com/gui/index.html?v=1.2.1.3583&localauth=localapibf2ae50bd9195d86:#/library")
            time.sleep(10)
            add_torrent_btn = browser.find_element_by_class_name("""upload-btn-text""")
            add_torrent_btn.click()
            time.sleep(3)
            magnet_placeholder = browser.find_element_by_class_name("""link-input""")
            magnet_placeholder.send_keys(magnet_url)
            time.sleep(3)
            add_torrent_url_btn = browser.find_element_by_id("""add-torrent-url-btn""")
            add_torrent_url_btn.click()
            time.sleep(3)
            final_add_btn = browser.find_element_by_css_selector(
                """#add-torrent-modal > div.modal-two-button-footer > 
                button.add-torrent-btn.modal-footer-right-button.button--secondary""")
            final_add_btn.click()
            break
        except:
            browser.refresh()


if __name__ == '__main__':

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
                print()
                Checker(intervals_for_checking, user_info)
    except:
        print("\n\nAn error occurred: ")
        traceback.print_exc()
