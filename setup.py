import pickle
from Main import UserInfo

if __name__ == "__main__":
    initial_user = UserInfo("Blank", "Blank", "Blank", True)
    with open("user_info_file", "wb") as file:
        pickle.dump(initial_user, file)
