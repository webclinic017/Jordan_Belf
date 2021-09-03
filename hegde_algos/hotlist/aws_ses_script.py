import emails

# Prepare the email
message = emails.html(
    html="<h1>This month's top picks</h1><strong>AAPL, MAC, AMD, NVDA</strong>",
    subject="HOTLIST",
    mail_from="jordanbelf2021@gmail.com",
)

# Send the email
r = message.send(
    to="mhmccoy2017@gmail.com", 
    smtp={
        "host": "email-smtp.us-east-2.amazonaws.com", 
        "port": 587, 
        "timeout": 5,
        "user": "AKIA4STHFKDGBZY3YBOV",
        "password": "BP4RNOGRipdzOSIj0xNgiDKD2oNe6rqqIExN57fyF8td",
        "tls": True,
    },
)

# Check if the email was properly sent
assert r.status_code == 250  

print(r.status_code)
