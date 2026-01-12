import os    # for file handling  
import sys   # for writing/printing messages
import math

import re    # for splitting input

from file_utils import remove_file, rename_file, DISK_PATH

######### CONSTANTS (unlimited number allowed) #######################
PATH = os.path.join(DISK_PATH, "") # path to store files (DO NOT CHANGE)
TEMPORARY = os.path.join(DISK_PATH, "temporary.txt")
SWITCH = os.path.join(DISK_PATH, "switch.txt")
METADATA = os.path.join(DISK_PATH, "metadata.txt")
SEP = "====" # used to separate messages when printing them out


######### VARIABLES (at most 10 active at any time) ##################

######### EXCEPTIONS #################################################
class MessagesFullExn(Exception):
    pass

######### SYSTEM SETUP, SHUTDOWN, AND RESET ##########################
number_of_messages = 0
current = ""
def connect(username: str, restart: bool) -> None:
    """
    Starts a connection to the system by the named user

    Parameters:
    username -- the name of the user who is connecting (they will be the
                poster of messages added until they disconnect)
    restart -- if the program has just connected to the server
    """
    # TODO: Fill in!
    global current
    #os.chdir("/Users/avinash_a_patel/Desktop/cs200/hw05-information-JediKnight007/sol") 
    if not os.path.exists(DISK_PATH):
        os.mkdir(DISK_PATH)
    current = username
    if restart is True:
        with open(METADATA, "a") as f:
            for n in range(200):
                f.write(str(n+1) + "\n")


def disconnect() -> None:
    """
    Disconnects the current user (this will depend on your design) and saves
    data as necessary so that the system can resume even if the Python program
    is restarted 
    """
    global current
    current = ""
    SystemExit



def soft_disconnect() -> None:
    """
    Disconnects the current user (this will depend on your design)
    """
    global current
    current = ""


def clean_reset(msg_max_val=200, msg_per_file_val=10) -> None:
    """
    Deletes all the disk files to start a clean run of the system.
    Supports setting different constant values.
    Useful for testing.

    Parameters:
    msg_max_val -- max number of messages system can hold
    msg_per_file_val -- max number of messages each file can hold

    """
    
    # TODO: Fill in with what makes sense for your design.
    # It might relate to how you store your necessary info
    # between (dis)connections to the server!
    # Feel free to pass in different values when testing for clean_reset,
    # 200 and 10 are just the default. (You do not need to edit
    # the method header to do this. Just pass different values in when calling)

    #os.chdir("/Users/avinash_a_patel/Desktop/cs200/hw05-information-JediKnight007/sol") 
    if os.path.exists(DISK_PATH):
        for files in os.scandir(DISK_PATH):
            remove_file(files)
    else:
        os.mkdir(DISK_PATH)
    



######## DESIGN HELPERS ##########################################
def write_msg(f, id: int, who: str, subj: str, msg: str, labeled=False) -> None:
    """
    Writes a message to the given file handle. e.g., If you want to print to a
    file, open the file and use fh from the following code as the first argument

           with open(FILENAME, mode) as fh

    If you want to print to the console/screen, you can pass the following as 
    the first argument

            sys.stdout

    msg can be passed as false to suppress printing the text/body of the message.

    Parameters:
    f -- file descriptor
    id -- message id
    who -- poster
    subj -- subject line
    msg -- body text
    labeled -- boolean deciding if labels should also be used
    """
    f.write(SEP + "\n")
    f.write("ID: " + str(id) + "\n")
    if labeled:
        f.write(who)
        f.write(subj)
        if msg: f.write(msg)
    else: # needs labels
        f.write("Poster: " + who + "\n")
        f.write("Subject: " + subj + "\n")
        if msg: f.write("Text: " + msg + "\n")


def split_string_exclude_quotes(s) -> list[str]:
    """
    Splits a given string and splits it based on spaces, while also grouping
    words in double quotes together.

    Parameters:
    s -- string to be split
    Returns:
    A list of strings after splitting
    Example:
    'separate "these are together" separate` --> ["separate", "these are together", "separate"]
    """
    # This pattern matches a word outside quotes or captures a sequence of characters inside double quotes without including the quotes
    pattern = r'"([^"]*)"|(\S+)'
    matches = re.findall(pattern, s)
    # Each match is a tuple, so we join non-empty elements
    return [m[0] if m[0] else m[1] for m in matches]


####### CORE SYSTEM OPERATIONS ####################################


def show_menu(): 
    """
    Prints the menu of options.
    """
    print("Please select an option: ")
    print("  - type A <subj> <msg> to add a message")
    print("  - type D <msg-num> to delete a message")
    print("  - type S for a summary of all messages")
    print("  - type S <text> for a summary of messages with <text> in title or poster")
    print("  - type V <msg-num> to view the contents of a message")
    print("  - type X to exit (and terminate the Python program)")
    print("  - type softX to exit (and keep the Python program running)")


def post_msg(subj: str, msg: str) -> None:
    """
    Stores a new message (however it makes sense for your design). Your code
    should determine what ID to use for the message, and the poster of the
    message should be the user who is connected when this function is called

    Parameters:
    subj -- subject line
    msg -- message body
    """
   
    # TODO: Fill in!
    global number_of_messages
    global current

    if subj == "" or msg == "" or len(subj) > 32: raise ValueError

    if number_of_messages > 200: raise MessagesFullExn
    
    with open(METADATA, "r") as f: id_number = f.readline()
       
    with open(TEMPORARY, "a") as file:
        with open(METADATA, "r") as files:
            curr_line = files.readline()
            while curr_line != "": 
                if curr_line != id_number:
                     file.write(curr_line)
                curr_line = files.readline()
    remove_file(METADATA)
    rename_file(TEMPORARY, METADATA)

    number_of_messages += 1

    writer(id_number, id_number, subj, msg)
    writer(id_number, 214, subj, msg)


#Writes ID files and summaries     
def writer(id: int, sum_num: int, subject: str, message: str):
    with open(os.path.join(DISK_PATH, f"{(int(sum_num) // 10) + 1}.txt"), "a") as f:
        f.write(str(id) + current + "/" + subject + "/" + "\n")
        if(sum_num != 214):
            f.write(message + "\n")

def find_print_msg(id: int) -> str:
    """
    Prints contents of message for given ID. 

    Parameters:
    id -- message ID
    Returns:
    The string to be printed (for autograder).
    """

    printed = ""
    ongoing = True
    with open(os.path.join(DISK_PATH, f"{(id // 10) + 1}.txt"), "r") as file:
        while ongoing is True:
            curr_line = file.readline()
            if curr_line == "":
                ongoing = False
                continue
            if curr_line != str(id) + "\n":
                file.readline()
                file.readline()
            else:
                curr_line_next = file.readline().split('/')
                printed += "ID: " + curr_line + "Poster: " + curr_line_next[0] + "\n" + "Subject: " + curr_line_next[1] + "Text: " + file.readline()
    return printed
            

def remove_msg(id: int) -> None:
    """
    Removes a message from however your design is storing it. A removed message
    should no longer appear in summaries, be available to print, etc.
    """
    global number_of_messages

    number_of_messages -= 1

    looper(id, id)
    looper(id, 214)

    with open(METADATA, "a") as file:
        file.write(str(id) + "\n")
    
#Method used to remove data by message ID from file_id file and summary file
def looper(id_num: int, sum_num: int):
    id_number = sum_num
    ongoing = True
    with open(SWITCH, "w") as file:
        with open(os.path.join(DISK_PATH, f"{(id_number // 10) + 1}.txt"), "r") as f:
           while ongoing == True:
                curr_line = f.readline()
                if curr_line == "":
                    ongoing = False
                    continue
                if curr_line == str(id_num) + "\n":
                    f.readline()
                    if(sum_num != 214):
                        f.readline()
                else:
                    file.write(curr_line)
        remove_file(os.path.join(DISK_PATH, f"{(id_number // 10) + 1}.txt"))
        rename_file(SWITCH, os.path.join(DISK_PATH, f"{(id_number // 10) + 1}.txt"))


def print_summary(term = "") -> str:
    """
    Prints summary of messages that have the search term in the who or subj fields.
    A search string of "" will match all messages.
    Summary does not need to present messages in order of IDs.

    Returns:
    A string to be printed (for autograder).
    """

    sum = ""
    ongoing = True
    if not os.path.exists(os.path.join(DISK_PATH, f"{(214 // 10) + 1}.txt")):
        return sum
    
    with open(os.path.join(DISK_PATH, f"{(214 // 10) + 1}.txt"), "r") as file:
        while ongoing is True:
            id = file.readline()
            if id == "":
                ongoing = False
                continue
            curr_line_next = file.readline()
            if term in curr_line_next:
                sum += "ID: " + id + "Poster: " + curr_line_next.split('/')[0] + "\n" + "Subject: " + curr_line_next.split('/')[1] + "\n"
    return sum
                

    
    # TODO: Fill in!


############### SAMPLE FROM HANDOUT ######################

# Our test cases will look like this, with assertions intertwined

def sample():
    connect("kathi", True)
    post_msg("post homework?", "is the handout ready?")
    post_msg("vscode headache", "reinstall to fix the config error")
    soft_disconnect()  # keep the python programming running and connect another user
    connect("nick", False)
    print_summary("homework")
    find_print_msg(1)
    post_msg("handout followup", "yep, ready to go")
    remove_msg(1)
    print_summary()
    disconnect()

############### MAIN PROGRAM ############################

# If you want to run the code interactively instead, use the following:

def start_system():
    """
    Loop to run the system. It does not do error checking on the inputs that
    are entered (and you do not need to fix that problem)
    """
    
    print("Welcome to our BBS!")
    print("What is your username?")
    connect(input(), True)

    done = False
    while(not done):
        show_menu()
        whole_input = input() # read the user command
        choice = split_string_exclude_quotes(whole_input) #split into quotes
        match choice[0].upper():
            case "A": 
                post_msg(choice[1], choice[2]) # subject, text
            case "D": 
                remove_msg(int(choice[1]))
            case "S": 
                if len(choice) == 1:
                    print_summary("")
                else:
                    term = choice[1]
                    print_summary(term)
            case "V":
                find_print_msg(int(choice[1]))
            case "X": 
                disconnect()
                done = True
                exit()
            case "SOFTX":
                soft_disconnect()

                # restart menu 
                print("What's your username?")
                connect(input(), False)
            case _: 
                print("Unknown command")

# uncomment next line if want the system to start when the file is run
#start_system()
