import urllib.request
s = urllib.request.urlopen("http://localhost:3000").read()
print(s)
