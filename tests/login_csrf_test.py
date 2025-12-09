import http.client
from http.client import HTTPConnection
from urllib.parse import urlencode
from html.parser import HTMLParser
import http.cookiejar as cookiejar
import urllib.request

LOGIN_URL = 'http://127.0.0.1:8000/login/'

class CSRFParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.csrf = None
    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            attrd = dict(attrs)
            if attrd.get('name') == 'csrfmiddlewaretoken':
                self.csrf = attrd.get('value')

def get_csrf_and_cookies():
    cj = cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(LOGIN_URL, headers={'User-Agent': 'test-client'})
    with opener.open(req) as resp:
        html = resp.read().decode('utf-8')
    parser = CSRFParser()
    parser.feed(html)
    csrf = parser.csrf
    cookies = {c.name: c.value for c in cj}
    return csrf, cookies, opener


def post_login(csrf, cookies, opener):
    data = {
        'username': 'fake@example.com',
        'password': 'wrongpassword',
        'csrfmiddlewaretoken': csrf,
    }
    encoded = urlencode(data).encode('utf-8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'test-client',
        'Referer': LOGIN_URL,
    }
    req = urllib.request.Request(LOGIN_URL, data=encoded, headers=headers)
    try:
        with opener.open(req) as resp:
            print('POST response code:', resp.getcode())
            print(resp.read().decode('utf-8')[:500])
    except urllib.error.HTTPError as e:
        print('HTTPError:', e.code)
        body = e.read().decode('utf-8')
        print(body[:500])

if __name__ == '__main__':
    csrf, cookies, opener = get_csrf_and_cookies()
    print('CSRF token:', csrf)
    print('Cookies:', cookies)
    post_login(csrf, cookies, opener)
