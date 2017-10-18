import re
import sys
import config

from getpass import getpass
from clients import smtp_client
from clients import imap_client
from exceptions.auth_error import AuthError

EMAIL_REGEX = "^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$"

class MailClient(object):

    def __init__(self, default=None):
        self.default = default
        self.logged_in = False
        self.menu_options = [
            self.toggle_log,
            self.read,
            self.write,
            self.settings,
            self.exit
        ]

        if self.default:
            self.default = True
            self.user = 'dcnfall2017.testing@gmail.com'
            self.password = 'dcnfall2017'

    def run(self):
        print("\nWelcome to pyMail\n")

        while True:
            self.main_menu()

            try:
                select = int(input("\nEnter your selection: "))
                # call function from func_list 'menu_options'
                self.menu_options[int(select)-1]()
            except(IndexError, ValueError):
                print("Invalid input. Try again.")

    def main_menu(self):
        if self.logged_in:
            toggle = "Logout"
        else:
            toggle = "Login"
        
        print("[1]{}\n[2]Read\n[3]Write\n[4]Settings\n[5]Exit".format(toggle))

    def toggle_log(self):
        if self.logged_in:
            self.logout()
        else:
            self.login()

    def login(self):
        if not self.logged_in:

            if not self.default:
                self.user = input("username: ")
                
                while not re.match(EMAIL_REGEX, self.user):
                    print("Invalid e-mail address. Try again.")
                    self.user = input("username: ");
                self.password = getpass();

            # If supporting other providers, parse domain here
            # then lookup smtp hostname and pass to client

            self.smtp = smtp_client.SMTPClient()
            self.imap = imap_client.IMAPClient()

            print("\nLogging in...\n")
            try:
                self.smtp.login(self.user, self.password)
                self.imap.login(self.user, self.password)
                self.logged_in = True
                print("Logged in as {}\n".format(self.user))
            except AuthError as e:
                print(e.message)
            
        else:
            print("\nYou're already logged in as {}\n".format(self.user))


    def logout(self):
        if self.logged_in:
            print("\nLogging out {}\n".format(self.user))
            if not self.default:
                self.user = None
                self.password = None
            self.logged_in = False
            self.smtp.quit()
            self.imap.quit()
        else:
            print("\nYou're not logged in.\n")

    def read(self):
        if not self.logged_in:
            print("\nYou need to login to read mail.\n")
            return

        self.imap.read()

    def write(self):
        if not self.logged_in:
            print("\nYou need to login to write mail.\n")
            return

        to = input("To: ")
        cc, bcc = self.add_cc_bcc()
        recipients = self.combine_recipients(to, cc, bcc)

        subject = input("Subject: ")
        body = ""
        print("Write your message here.\n"
              + "macOS/Linux: press Ctrl+D to finish.\n"
              + "Windows: press Ctrl+Z to finish.\n")
        for line in sys.stdin:
            body += line
      
        msg = self.smtp.compose(self.user, to, cc, subject, body)
        ok_to_send = self.print_preview(msg, body, bcc) 

        if ok_to_send: 
            print("\nSending message...\n")
            self.smtp.send(recipients, msg)
        else:
            print("\nCancelling message...\n")

    def add_cc_bcc(self):
        while True:
            yn = input("Add cc/bcc [y/n] ? ")
        
            if yn == 'y':
                cc = input("CC: ")
                bcc = input("BCC: ")
                return cc, bcc
            elif yn == 'n':
                return None, None
            else:
                print("Invalid input. Try again.")

    def combine_recipients(self, to, cc=None, bcc=None):
        recipients = to.split(", ")

        if cc:
            recipients += cc.split(", ")

        if bcc:
            recipients += bcc.split(", ")

        return recipients

    def print_preview(self, msg, body, bcc=None):
        print('\n*** Message Preview ***\n');
        print('From: {}\nTo: {}'.format(msg['From'], msg['To']))
        if 'cc' in msg.keys():
            print('Cc: {}'.format(msg['cc']))
        if bcc:
            print('Bcc: {}'.format(bcc))
        print('Subject: {}\nBody:\n{}\n'.format(msg['Subject'], body))

        choice = None
        while not choice:
            choice = input("Send message [y/n]?")

            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid input. Try again.")
                choice = None


    def settings(self):
        print("\n######## CURRENT SETTINGS ########")

        print("\n### IMAP ###")
        for val in config.imap:
            print("%-20s: %s" % (val.upper(), config.imap[val]))

        print("\n### SMTP ###")
        for val in config.smtp:
            print("%-20s: %s" % (val.upper(), config.smtp[val]))

        print("\n### GENERAL ###")
        for val in config.settings:
            print("%-20s: %s" % (val.upper(), config.settings[val]))

        print("\n")

    def exit(self):
        if self.logged_in:
            self.logout()
        print("\nGoodbye.\n")
        sys.exit(0)
