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

    def warning(self, msg: str):
        if msg.isprintable() and msg != "":
            print(f"{bcolors.WARNING}[WARNING]: {msg}{bcolors.ENDC}")

    def okblue(self, msg: str):
        if msg.isprintable() and msg != "":
            print(f"{bcolors.OKBLUE}[System]: {msg}{bcolors.ENDC}")

    def error(self, msg: str):
        if msg.isprintable() and msg != "":
            print(f"{bcolors.FAIL}[ERROR]: {msg}{bcolors.ENDC}")

    def error_imp(self, msg: str):
        print(f"{bcolors.FAIL}{bcolors.BOLD}[ERROR]: {msg}{bcolors.ENDC}")

    def info(self, msg: str):
        print(f"{bcolors.OKGREEN}[Info]: {msg}{bcolors.ENDC}")

    def msg(self,msg: str):
        print(f"        {msg}")

