About
=====

This is a plugin that creates a new channel in Plex Media Server to view content indexed by the website G2G.fm.

[Plex Support Thread](https://forums.plex.tv/discussion/111730/rel-g2g-fm-watch-latest-release-hd-movies-and-tv-series/p1)

**Note:** The author of this plugin has no affiliation with G2G.fm or the owners of the content that it indexes.

System Requirements
===================

- **Plex Media Server:**

	- Tested Working:
		- Windows
		- Mac OSX
		- Linux

- **Plex Clients:**

	- Tested Working:
		- Plex Home Theater
		- Plex/Web
		- Android
		- Chromecast
        - Ouya
		- Roku
		- iOS
		- PlexConnect
		- Smart TV

	- Not Tested:
		- Windows 8
		- Xbox
		- Windows Phone


How To Install
==============

- Download the latest version of the plugin.

- Unzip and rename folder to "G2Gfm.bundle"

- Copy G2Gfm.bundle into the PMS plugins directory under your user account:
	- Windows 7, Vista, or Server 2008: C:\Users[Your Username]\AppData\Local\Plex Media Server\Plug-ins
	- Windows XP, Server 2003, or Home Server: C:\Documents and Settings[Your Username]\Local Settings\Application Data\Plex Media Server\Plug-ins
	- Mac/Linux: ~/Library/Application Support/Plex Media Server/Plug-ins

- Restart PMS

Known Issues
============

- No item summaries.
- ~~No metadata info on final video page due to Google Video link.~~
- Source website has missing videos for some older content.


Changelog
=========

**0.11** - 10/13/2017 (2000 GMT) - CA's fork - Fixed proxy support

**0.11** - 10/12/2017 - CA's fork - Site changes / added client.py for HTTP/parsing operations

**0.11** - 07/25/2017 - CA's fork - [Local URL Service using Direct file method](https://github.com/coder-alpha/G2Gfm.bundle)

**0.11** - 07/24/2017 - CA's fork - Updated URLs and code for proxy

**0.11** - 11/01/2016 - Twoure's fork [Local URL Service](https://github.com/Twoure/G2Gfm.bundle/tree/dev)

**0.11** - 09/18/16 - Updated mirror URL from g2gfm.eu to proxyunblocker.org and proxywebsite.co.uk. (https://github.com/TehCrucible/G2Gfm.bundle/archive/master.zip)

**0.10** - 07/22/16 - Updated URL to cyro.se. Added back Search function.

**0.09** - 06/17/16 - Added back TV Shows and Latests Episodes. Fixed video parse code.

**0.08** - 06/08/16 - Fixed code for site changes. Added Site URL preference.

**0.07** - 08/29/15 - Updated URL to dayt.se.

**0.06** - 08/23/15 - Updated URL to atoz.se.

**0.05** - 14/07/15 - Updated URL to moviez.se.

**0.04** - 19/11/14 - Removed search and bookmarks.

**0.03** - 14/06/14 - Added genres menu. Removed item summaries due to bugs.

**0.02** - 11/06/14 - Added trailers, search and bookmarks. Removed URL service.

**0.01** - 09/06/14 - Initial release.
