from GoogleNews import GoogleNews
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


sender_email = "xxx@gmail.com" #replace
receiver_email = "xxx@gmail.com"
password = "xxx" #myaccount.google.com/apppasswords create app password do not use account pwd
server_str = 'smtp.gmail.com'
port_num = 587

today = datetime.now()+ pd.Timedelta(days=1)
googlenews = GoogleNews()
googlenews.enableException(True)
googlenews = GoogleNews(lang='en', region='US')
yesterday = today - pd.Timedelta(days=2)
week_ago = today - pd.Timedelta(days=8)
today_dt = today.strftime('%m/%d/%Y')
yesterday_dt = yesterday.strftime('%m/%d/%Y')
week_ago_dt = week_ago.strftime('%m/%d/%Y')

googlenews_1d = GoogleNews(start=yesterday_dt, end=today_dt)
googlenews_1d.get_news('Federal Reserve')
result_1d=googlenews_1d.result(sort=True)

googlenews_7d = GoogleNews(start=week_ago_dt, end=yesterday_dt)
googlenews_7d.get_news('Federal Reserve')
result_7d=googlenews_7d.result(sort=True)


df_1d=pd.DataFrame(result_1d)
df_7d=pd.DataFrame(result_7d)

media_sources = ['Financial Times', 'Bloomberg', 'The Wall Street Journal', 'The New York Times']
pattern = '|'.join(media_sources)
df_1d = df_1d[df_1d['media'].str.contains(pattern, case=False)]
df_1d = df_1d.drop_duplicates(subset=['title'])
df_1d = df_1d[['title', 'date', 'media', 'link']]

df_7d = df_7d[df_7d['media'].str.contains(pattern, case=False)]
df_7d = df_7d.drop_duplicates(subset=['title'])
df_7d = df_7d[['title', 'date', 'media', 'link']]
df_7d

def df_to_html_with_styles(df):
    if df.empty:
      return "<p>No news update</p>"
    else:
      df.style.set_properties(subset=['title'], **{'width': '3000px'})
      html = df.to_html(index=False, escape=False)
      
      html = html.replace('<th>', '<th style="text-align: left;">')
      html = html.replace('<td>', '<td align="left">')
      html = html.replace('<td style="width: 300px;">', '<td style="width: 300px;"><b>').replace('</td>', '</b></td>', 1)
      return html

html = f"""\
<html>
  <head></head>
  <body>
    <h2>Past 24 Hours:</h2>
    {df_to_html_with_styles(df_1d)}
    <br>
    <h2>Older (7d):</h2>
    {df_to_html_with_styles(df_7d)}
  </body>
</html>
"""

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "Fed News Alert"

part1 = MIMEText(html, 'html')
msg.attach(part1)

# Send email
try:
    server = smtplib.SMTP(server_str, port_num)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("Email sent successfully")
except Exception as e:
    print(f"Failed to send email: {e}")
