class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Debug:

    def __init__(self) -> None:
        pass

    @staticmethod
    def warning(msg: str):
        if msg.isprintable() and msg != "":
            print(f"{bcolors.WARNING}[WARNING]: {msg}{bcolors.ENDC}")

    @staticmethod
    def okblue(msg: str):
        if msg.isprintable() and msg != "":
            print(f"{bcolors.OKBLUE}[System]: {msg}{bcolors.ENDC}")

    @staticmethod
    def error(msg: str):
        if msg.isprintable() and msg != "":
            print(f"{bcolors.FAIL}[ERROR]: {msg}{bcolors.ENDC}")

    @staticmethod
    def error_imp(msg: str):
        print(f"{bcolors.FAIL}{bcolors.BOLD}[ERROR]: {msg}{bcolors.ENDC}")

    @staticmethod
    def info(msg: str):
        print(f"{bcolors.OKGREEN}[Info]: {msg}{bcolors.ENDC}")

    @staticmethod
    def msg(msg: str):
        print(f"        {msg}")
