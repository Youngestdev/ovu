import os
import resend

resend.api_key = "re_H1JtKmeQ_P2JcSWpsxb6PWkC3NWkWPwS1"

params: resend.Emails.SendParams = {
    "from": "Ovu Transport <noreply@ovu.ng >",
    "to": ["youngestdev@gmail.com"],
    "subject": "hello world",
    "html": "<strong>it works!</strong>",
}

email = resend.Emails.send(params)
print(email)