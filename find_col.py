import httpx
import re
r = httpx.get('https://gearvn.com', follow_redirects=True).text
matches = set(re.findall(r'/collections/(laptop[^\"\'><?]+)', r))
for m in matches:
    print(m)
