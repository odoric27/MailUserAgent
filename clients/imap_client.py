import imaplib
import ssl
import config
import email

from exceptions.auth_error import AuthError

class IMAPClient(object):
    def __init__(self,
                 host=None,
                 port=None,
                 require_ssl=None):

        if not host:
            self.host = config.imap["host"]
        else:
            self.host = host

        if require_ssl is None:
            require_ssl = config.imap["require_ssl"]

        if require_ssl:
            self.ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)

            if not port:
                self.port = config.imap["ssl_port"]
            else:
                self.port = port
                
            self.client = imaplib.IMAP4_SSL(host=self.host,
                                            port=self.port,
                                            ssl_context=self.ctx)
        else:
            self.ctx = None

            if not port:
                self.port = config.imap["port"]
            else:
                self.port = port

            self.client = imaplib.IMAP4(host=self.host,
                                        port=self.port)

    def login(self, user, password):
        try:
            self.client.login(user, password)
        except imaplib.IMAP4.error:
            raise AuthError()

    def read(self):
        _, total = self.client.select('INBOX', readonly=True)
        total = int(total[0])
        msg_count = 1
        remaining = total
        max_display = config.settings["inbox_display_size"]

        if total < max_display:
            max_display = total
        
        has_next_batch = True if total > max_display else False
        has_prev_batch = True if remaining < total else False

        print("\nYou have %s messages" % total)
        print("Displaying first {} messages".format(max_display))
        self.display_message_range(max_display, msg_count, total)

        while has_next_batch or has_prev_batch:
            if has_prev_batch:
                print("[1] Go back\n[2] Next page\n[3] Previous page")
            else:
                print("[1] Go back\n[2] Next page")
            select = input("Enter your selection: ")
            
            if select == '1':
                print("\n")
                break
            elif select == '2':
                remaining -= max_display
                msg_count += max_display
            elif select == '3':
                remaining += max_display
                msg_count -= max_display
            else:
                print("\nInvalid input. Try again.\n")
                continue

            has_next_batch = True if remaining > max_display else False
            has_prev_batch = True if remaining < total else False

            self.display_message_range(max_display, msg_count, remaining)


    def display_message_range(self, max_display, msg_count, total):
        for i in range(0, max_display):
            _, msg_data = self.client.fetch(str(total - i), '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    print('%-8s: %s\n' % ('MESSAGE', (msg_count + i)))
                    for header in ['TO', 'FROM', 'SUBJECT']:
                        print('%-8s: %s' % (header, msg[header]))
                    print('\n%-8s: %s' % 
                        ('PREVIEW', self.display_body_preview(msg)))
                    self.separator()

    def display_body_preview(self, msg):
        body = self.get_body_text(msg)
        return self.shorten(body)

    def get_body_text(self, msg):
        if msg['Content-Type'].startswith('text/plain'):
            return self.shorten(msg.get_payload())

        if(isinstance(msg, email.message.Message) and msg.is_multipart()):
            payload = msg.get_payload()
            for p in payload:
                return self.get_body_text(p)
        else:
            return 'Error: could not display message'

    def separator(self):
        line = ''
        for i in range(81):
            line += '-'
        print(line)

    def shorten(self, body):
        if len(body) > 70:
            body = body[:68] + '...'
        return body

    def quit(self):
        self.client.logout()