import smtplib, os,sys, email.message, datetime
from dotenv import load_dotenv
class email_util:
    @staticmethod
    def send(message_body):

        load_dotenv('/Users/franserr/Documents/portfolio/spotify_usage/env_files/sender.env')
        try:

            sender_email = os.environ['sender_email']
            password = os.environ['sender_pw']
        except:
            sys.exit(1)
        receiver_email = "fjs@cpp.edu"

        message = message_body
        message=message.encode('utf-8')

        try:
            
            
            smtpObj = smtplib.SMTP("smtp.gmail.com", 587)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(sender_email, password)
            this_month=datetime.datetime.now().strftime('%B')
            msg=email.message.Message()
            msg['Subject']= 'Your '+this_month+ '\'s Listening History'
            msg['From']=sender_email
            msg['To']=receiver_email
            msg.add_header('Content-Type', 'text/plain')
            msg.set_payload(message)

            smtpObj.send_message( msg=msg, )         
            print("email got sent")
        except Exception as e:
            print("Error: Unable to send email")
            print(e)

        smtpObj.quit()

        pass





