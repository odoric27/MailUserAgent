import smtplib
import config
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from exceptions.auth_error import AuthError

class SMTPClient(object):
    def __init__(self,
                 host=None,
                 port=None,
                 require_ssl=None):

        if not host:
            self.host = config.smtp["host"]
        else:
            self.host = host

        if require_ssl is None:
            require_ssl = config.smtp["require_ssl"]

        if require_ssl:
            self.ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)

            if not port:
                self.port = config.smtp["ssl_port"]
            else:
                self.port = port
               
            self.client = smtplib.SMTP_SSL(host=self.host,
                                           port=self.port,
                                           context=self.ctx)
        else:
            self.ctx = None

            if not port:
                self.port = config.smtp["port"]
            else:
                self.port = port

            self.client = smtplib.SMTP(host=self.host,
                                       port=self.port)


    def login(self, user, password):
        try:
            self.client.login(user, password)
        except smtplib.SMTPAuthenticationError:
            raise AuthError()

    def send(self, recipients, msg):
        try:
            self.client.ehlo_or_helo_if_needed()

            if not self.ctx:
                self.client.starttls()
                self.client.ehlo_or_helo_if_needed()

            self.client.sendmail(msg['From'], recipients, msg.as_string())
            print("Message sent.\n")
        except(smtplib.SMTPException) as e:
            print("Couldn't send message... Error: {}\n".format(e.args))


    def compose(self, sender, to, cc=None, subj=None, body=None):
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = to
        
        if cc:
            msg["CC"] = cc

        if subj:
            msg['Subject'] = subj

        if body:
            msg.attach(MIMEText(body))

        return msg

    def quit(self):
        self.client.quit()

