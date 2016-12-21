# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import mechanize
import cookielib

# <codecell>

    import mechanize
    import cookielib

# <codecell>

import mechanize
import cookielib

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# <codecell>

url='http://www.republicservices.com/residents'

# <codecell>

# Open some site, let's pick a random one, the first that pops in mind:
r = br.open(url)
html = r.read()

# Show the source
print html
# or
print br.response().read()

# Show the html title
print br.title()

# <codecell>

# Show the response headers
print r.info()
# or
print br.response().info()

# <codecell>

# Show the available forms
for f in br.forms():
    print f

# Select the first (index zero) form
br.select_form(nr=0)

# <codecell>

# Let's search
br.form['q']='weekend codes'

# <codecell>

br.submit()
print br.response().read()

# Looking at some results in link format
for l in br.links(url_regex='stockrt'):
    print l

# <codecell>


# <codecell>

https://api.smartystreets.com/street-address?auth-id=06ddff4c-dec1-4e5e-a580-b349c89439a1&auth-token=bTOYHFJTotZnfzANl5wwa/QjzDym0jhIIX/sSGWiy6DanZBS6cz5daCFoZMSNEQmLGboKaDqidVPj9GNo0m6eg==&callback=jQuery211009337028139270842_1423485492638&street=81+Queen+Street&zipcode=02540&candidates=10&_=1423485492639

