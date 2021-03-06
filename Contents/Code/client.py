#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################################################
#
# Client lib
#
# Coder Alpha
# https://github.com/coder-alpha
#
#
#########################################################################################################

import re, json
import sys,urllib2,HTMLParser,urllib,urlparse
import random, time, cookielib
import base64

from __builtin__ import eval


#-------------------------------------------------------------------------------------------------------------
# Enforce IPv4 for GetlinkAPI nks Google li
# do this once at program startup
# Reference: http://stackoverflow.com/questions/2014534/force-python-mechanize-urllib2-to-only-use-a-requests
#--------------------
import socket
origGetAddrInfo = socket.getaddrinfo

def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
	return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

# #replace the original socket.getaddrinfo by our version
# socket.getaddrinfo = getAddrInfoWrapper
# socket.has_ipv6 = False
#-------------------------------------------------------------------------------------------------------------

GLOBAL_TIMEOUT_FOR_HTTP_REQUEST = 15
HTTP_GOOD_RESP_CODES = ['200','206']
	
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0"
IE_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
IOS_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
ANDROID_USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
#SMU_USER_AGENT = 'URLResolver for Kodi/%s' % (addon_version)

IP_OVERIDE = True

def request(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, XHR=False, IPv4=False):

# output extended = 4, response = 2, responsecodeext = 2
	
	try:
		handlers = []
		redirectURL = url
		
		if IPv4 == True:
			setIP4()
		
		if error==False and not proxy == None:
			handlers += [urllib2.ProxyHandler({'http':'%s' % (proxy)}), urllib2.HTTPHandler]
			opener = urllib2.build_opener(*handlers)
			opener = urllib2.install_opener(opener)

		if error==False and output == 'cookie2' or output == 'cookie' or output == 'extended' or not close == True:
			cookies = cookielib.LWPCookieJar()
			if httpsskip or use_web_proxy:
				handlers += [urllib2.HTTPHandler(), urllib2.HTTPCookieProcessor(cookies)]
			else:
				handlers += [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
			opener = urllib2.build_opener(*handlers)
			opener = urllib2.install_opener(opener)
			
		try:
			if error==False:
				if sys.version_info < (2, 7, 9): raise Exception()
				import ssl; ssl_context = ssl.create_default_context()
				ssl_context.check_hostname = False
				ssl_context.verify_mode = ssl.CERT_NONE
				handlers += [urllib2.HTTPSHandler(context=ssl_context)]
				opener = urllib2.build_opener(*handlers)
				opener = urllib2.install_opener(opener)
		except:
			pass

		try: headers.update(headers)
		except: headers = {}
		if 'User-Agent' in headers:
			pass
		elif not mobile == True:
			#headers['User-Agent'] = agent()
			#headers['User-Agent'] = Constants.USER_AGENT
			headers['User-Agent'] = randomagent()		
		else:
			headers['User-Agent'] = 'Apple-iPhone/701.341'
		if 'Referer' in headers:
			pass
		elif referer == None:
			headers['Referer'] = '%s://%s/' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
		else:
			headers['Referer'] = referer
		if not 'Accept-Language' in headers:
			headers['Accept-Language'] = 'en-US'
		if 'X-Requested-With' in headers:
			pass
		elif XHR == True:
			headers['X-Requested-With'] = 'XMLHttpRequest'
		if 'Cookie' in headers:
			pass
		elif not cookie == None:
			headers['Cookie'] = cookie

		if error==False and redirect == False:
			class NoRedirection(urllib2.HTTPErrorProcessor):
				def http_response(self, request, response): 
					if IPv4 == True:
						setIP6()
					return response

			opener = urllib2.build_opener(NoRedirection)
			opener = urllib2.install_opener(opener)

			try: del headers['Referer']
			except: pass
			
		redirectHandler = None
		urlList = []
		if error==False and followredirect:
			class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):
				def redirect_request(self, req, fp, code, msg, headers, newurl):
					newreq = urllib2.HTTPRedirectHandler.redirect_request(self,
						req, fp, code, msg, headers, newurl)
					if newreq is not None:
						self.redirections.append(newreq.get_full_url())
					if IPv4 == True:
						setIP6()
					return newreq
			
			redirectHandler = HTTPRedirectHandler()
			redirectHandler.max_redirections = 10
			redirectHandler.redirections = [url]

			opener = urllib2.build_opener(redirectHandler)
			opener = urllib2.install_opener(opener)

		request = urllib2.Request(url, data=post, headers=headers)
		#print request

		try:
			response = urllib2.urlopen(request, timeout=int(timeout))
			if followredirect:
				for redURL in redirectHandler.redirections:
					urlList.append(redURL) # make a list, might be useful
					redirectURL = redURL
					
		except urllib2.HTTPError as response:
			
			try:
				resp_code = response.code
			except:
				resp_code = None
			
			try:
				content = response.read()
			except:
				content = ''
				
			if response.code == 503:
				#Log("AAAA- CODE %s|%s " % (url, response.code))
				if 'cf-browser-verification' in content:
					print("CF-OK")

					netloc = '%s://%s' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
					#cf = cache.get(cfcookie, 168, netloc, headers['User-Agent'], timeout)
					cfc = cfcookie()
					cf = cfc.get(netloc, headers['User-Agent'], timeout)
					
					headers['Cookie'] = cf
					request = urllib2.Request(url, data=post, headers=headers)
					response = urllib2.urlopen(request, timeout=int(timeout))
				elif error == False:
					if IPv4 == True:
						setIP6()
					return
				elif error == True:
					return '%s: %s' % (response.code, response.reason), content
			elif response.code == 307:
				#Log("AAAA- Response read: %s" % response.read(5242880))
				#Log("AAAA- Location: %s" % (response.headers['Location'].rstrip()))
				cookie = ''
				try: cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
				except: pass
				headers['Cookie'] = cookie
				request = urllib2.Request(response.headers['Location'], data=post, headers=headers)
				response = urllib2.urlopen(request, timeout=int(timeout))
				#Log("AAAA- BBBBBBB %s" %  response.code)
			elif resp_code != None:
				if IPv4 == True:
					setIP6()
				if output == 'response':
					return (resp_code, None)
				return resp_code
			elif error == False:
				#print ("Response code",response.code, response.msg,url)
				if IPv4 == True:
					setIP6()
				return
			else:
				if IPv4 == True:
					setIP6()
				return
		except Exception as e:
			print ('Error client.py>request : %s' % url)
			print ('Error client.py>request : %s' % (e.args))
			if IPv4 == True:
				setIP6()
			if output == 'response':
				return (None, None)
			return None

		if output == 'cookie':
			try: result = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
			except: pass
			try: result = cf
			except: pass

		elif output == 'response':
			if limit == '0':
				result = (str(response.code), response.read(224 * 1024))
			elif not limit == None:
				result = (str(response.code), response.read(int(limit) * 1024))
			else:
				result = (str(response.code), response.read(5242880))
				
		elif output == 'responsecodeext':
			result = (str(response.code),redirectURL)
			
		elif output == 'responsecode':
			result = str(response.code)

		elif output == 'chunk':
			try: content = int(response.headers['Content-Length'])
			except: content = (2049 * 1024)
			#Log('CHUNK %s|%s' % (url,content))
			if content < (2048 * 1024):
				if IPv4 == True:
					setIP6()
				return
			result = response.read(16 * 1024)
			if close == True: response.close()
			if IPv4 == True:
				setIP6()
			return result

		elif output == 'extended':
			try: cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
			except: pass
			try: cookie = cf
			except: pass
			content = response.headers
			result = response.read(5242880)
			if IPv4 == True:
				setIP6()
			return (result, headers, content, cookie)

		elif output == 'geturl':
			result = response.geturl()

		elif output == 'headers':
			content = response.headers
			if IPv4 == True:
				setIP6()
			return content

		else:
			if limit == '0':
				result = response.read(224 * 1024)
			elif not limit == None:
				result = response.read(int(limit) * 1024)
			else:
				result = response.read(5242880)

		if close == True:
			response.close()

		if IPv4 == True:
			setIP6()
		return result
		
	except Exception as e:
		print ('ERROR client.py>request %s, %s' % (e.args,url))
		if IPv4 == True:
			setIP6()
		return
		
def agent():
	return randomagent()

def randomagent():
	BR_VERS = [
		['%s.0' % i for i in xrange(18, 43)],
		['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111',
		 '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71',
		 '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80'],
		['11.0']]
	WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
	FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
	RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
				'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36']
	index = random.randrange(len(RAND_UAS))
	return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))
		
def setIP4(setoveride=False):

	if setoveride==False and IP_OVERIDE == True:
		return
	#replace the original socket.getaddrinfo by our version
	socket.getaddrinfo = getAddrInfoWrapper
	socket.has_ipv6 = False
	
def setIP6(setoveride=False):

	if setoveride==False and IP_OVERIDE == True:
		return
	#replace the IP4 socket.getaddrinfo by original
	socket.getaddrinfo = origGetAddrInfo
	socket.has_ipv6 = True

####################################################################################################
def parseDOM(html, name=u"", attrs={}, ret=False):
	# Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen

	if isinstance(html, str):
		try:
			html = [html.decode("utf-8")] # Replace with chardet thingy
		except:
			html = [html]
	elif isinstance(html, unicode):
		html = [html]
	elif not isinstance(html, list):
		return u""

	if not name.strip():
		return u""

	ret_lst = []
	for item in html:
		temp_item = re.compile('(<[^>]*?\n[^>]*?>)').findall(item)
		for match in temp_item:
			item = item.replace(match, match.replace("\n", " "))

		lst = []
		for key in attrs:
			lst2 = re.compile('(<' + name + '[^>]*?(?:' + key + '=[\'"]' + attrs[key] + '[\'"].*?>))', re.M | re.S).findall(item)
			if len(lst2) == 0 and attrs[key].find(" ") == -1:  # Try matching without quotation marks
				lst2 = re.compile('(<' + name + '[^>]*?(?:' + key + '=' + attrs[key] + '.*?>))', re.M | re.S).findall(item)

			if len(lst) == 0:
				lst = lst2
				lst2 = []
			else:
				test = range(len(lst))
				test.reverse()
				for i in test:  # Delete anything missing from the next list.
					if not lst[i] in lst2:
						del(lst[i])

		if len(lst) == 0 and attrs == {}:
			lst = re.compile('(<' + name + '>)', re.M | re.S).findall(item)
			if len(lst) == 0:
				lst = re.compile('(<' + name + ' .*?>)', re.M | re.S).findall(item)

		if isinstance(ret, str):
			lst2 = []
			for match in lst:
				attr_lst = re.compile('<' + name + '.*?' + ret + '=([\'"].[^>]*?[\'"])>', re.M | re.S).findall(match)
				if len(attr_lst) == 0:
					attr_lst = re.compile('<' + name + '.*?' + ret + '=(.[^>]*?)>', re.M | re.S).findall(match)
				for tmp in attr_lst:
					cont_char = tmp[0]
					if cont_char in "'\"":
						# Limit down to next variable.
						if tmp.find('=' + cont_char, tmp.find(cont_char, 1)) > -1:
							tmp = tmp[:tmp.find('=' + cont_char, tmp.find(cont_char, 1))]

						# Limit to the last quotation mark
						if tmp.rfind(cont_char, 1) > -1:
							tmp = tmp[1:tmp.rfind(cont_char)]
					else:
						if tmp.find(" ") > 0:
							tmp = tmp[:tmp.find(" ")]
						elif tmp.find("/") > 0:
							tmp = tmp[:tmp.find("/")]
						elif tmp.find(">") > 0:
							tmp = tmp[:tmp.find(">")]

					lst2.append(tmp.strip())
			lst = lst2
		else:
			lst2 = []
			for match in lst:
				endstr = u"</" + name

				start = item.find(match)
				end = item.find(endstr, start)
				pos = item.find("<" + name, start + 1 )

				while pos < end and pos != -1:
					tend = item.find(endstr, end + len(endstr))
					if tend != -1:
						end = tend
					pos = item.find("<" + name, pos + 1)

				if start == -1 and end == -1:
					temp = u""
				elif start > -1 and end > -1:
					temp = item[start + len(match):end]
				elif end > -1:
					temp = item[:end]
				elif start > -1:
					temp = item[start + len(match):]

				if ret:
					endstr = item[end:item.find(">", item.find(endstr)) + 1]
					temp = match + temp + endstr

				item = item[item.find(temp, item.find(match)) + len(temp):]
				lst2.append(temp)
			lst = lst2
		ret_lst += lst

	return ret_lst
	