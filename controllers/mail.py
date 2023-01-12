import smtplib
from pydantic import EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
from config import EMAIL, EMAIL_PASSWORD

def is_email_valid(email: str):
    try:
        validate_email(email)
    except EmailNotValidError:
        return False
    return True


fromaddr = EMAIL
mypassfromaddr = EMAIL_PASSWORD


def send_password_change_email(toaddr: EmailStr, url: str):
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Смена пароля"

    body = f"""<pre>
    <p>Если вы хотите изменить пароль, то перейдите по этой ссылке:</p>
    <a href='{url}'>Вот эта ссылка</a>
    <p>В противном случае игнорируйте это письмо</p>
    </pre>"""
    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(fromaddr, mypassfromaddr)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()