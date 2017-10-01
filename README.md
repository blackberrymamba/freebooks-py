# freebooks-py

Scripts for downloading free ebooks.
 1. woblink.com

-----

woblinkcom.py
===

Script for downloading free ebooks from woblink.com

### Install some modules:
 - requests
 - tqdm
 - bs4

### Usage:
<pre>
usage: woblinkcom.py [-h] -user USERNAME -pass PASSWORD [-dir DIRECTORY]  (--epub | --mobi)

Script for downloading free ebooks from woblink.com

optional arguments:
  -h, --help      show this help message and exit
  -user USERNAME  Username for Woblink.com
  -pass PASSWORD  Password for Woblink.com
  -dir DIRECTORY  Directory for download. Default: woblink
  --epub          Download EPUB. Default: false
  --mobi          Download MOBI. Default: false
  </pre>
