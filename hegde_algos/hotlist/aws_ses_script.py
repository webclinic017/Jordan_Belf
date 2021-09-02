import smtplib

s = smtplib.SMTP()

s.connect('email-smtp.us-east-2.amazonaws.com', 465)

s.starttls()

s.login('AKIA4STHFKDGBZY3YBOV', 'BP4RNOGRipdzOSIj0xNgiDKD2oNe6rqqIExN57fyF8td')

msg= 'From: jordanbelf2021@gmail.com\nTo: mhmccoy2017@gmail.com\nSubject: Test\n\n  This is a test'

s.sendmail('jordanbelf2021@gmail.com', 'mhmccoy2017@gmail.com', msg)
