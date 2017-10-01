import sys
import os
import argparse
from getpass import getpass
import requests
import json
from tqdm import tqdm
from bs4 import BeautifulSoup

class Woblink(object):
    def __init__(self, username, password, epub, mobi, directory, overwrite = False):
        self.username = username
        self.password = password
        self.epub = epub
        self.mobi = mobi
        self.directory = directory
        self.overwrite = overwrite
        self.authorized = False
        self.baseurl = "https://woblink.com"
        self.currentpage = 1
        self.maxpages = None
        self.session = requests.session()

    def login(self):
        if self.authorized == True:
            return

        url = self.baseurl + "/login"
        post_data = {
            "login[email]":self.username,
            "login[password]":self.password,
        }

        response = self.session.post(url, post_data)
        parsed_html = BeautifulSoup(response.text,'html.parser')
        logout_link = parsed_html.body.find('a', attrs={'href':'/user/logout'})
        error_list = parsed_html.body.find('ul', attrs={'class':'error_list'})
        if error_list is None and logout_link is not None:
            self.authorized = True
            print ("Login.")
        else:
            self.authorized = False
            print( "Login error: ", error_list.find("li").string )
            sys.exit(2)

    def logout(self):
        url= self.baseurl + "/user/logout"
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.text,'html.parser')
        logout_link = parsed_html.body.find('a', attrs={'href':'/user/logout'})
        if logout_link is None:
            print ("Logout")
            self.authorized = False
        else:
            print("Logout error...")

    def saveResponse(self,file, response):
        f = open(file, 'wt', encoding='utf-8')
        f.write(response.text)

    def getBooks(self):
        url= self.baseurl + "/publication/ajax?mode=free&page=" + str(self.currentpage) + "&query=&single_type=&where=&filtr=cena^0,0|type^ebook"
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.text,'html.parser')
        pages_max = parsed_html.find('input', {'type' : 'number','name':'page'})
        self.maxpages = int(pages_max.attrs['max'])
        print ("Page: ", self.currentpage, " z ", self.maxpages)
        for book in parsed_html.find_all('div', {'class' : 'nw_katalog_lista_ksiazka'}):
            item_data = {}
            item_data['title'] = book.select("h3.nw_katalog_lista_ksiazka_detale_tytul a")[0].text.title()
            item_data['author'] = book.select("p.nw_katalog_lista_ksiazka_detale_autor a")[0].text.title()
            item_data['description'] = book.select("p.nw_katalog_lista_ksiazka_detale_opis")[0].text
            item_data['price'] = book.select("div.nw_opcjezakupu_cena span.liczba")[0].text
            item_data['add_to_cart_link'] = book.select("a.nw_opcjezakupu_darmowa")[0].get("href")
            self.getItem(item_data)

        if self.currentpage < self.maxpages:
            self.currentpage = self.currentpage + 1
            self.getBooks()

    def downloadFile(self,url,filename):
        filename = "".join(x for x in filename if x not in "\/:*?<>|")

        if os.path.exists(self.directory + "/" + filename) and self.overwrite == False:
            print (filename, ": already exist.")
            return

        url = self.baseurl + url
        r = self.session.get(url, stream=True)
        total_length = r.headers.get('content-length')

        
        if total_length is None:
             total_length = 0
        with open(self.directory + "/" + filename, 'wb') as f:
            pbar = tqdm(desc=filename, total=int( total_length ), unit='B', unit_scale=True )
            for chunk in r.iter_content(1024):
                if chunk:
                    pbar.update (len(chunk))
                    f.write(chunk)
        return filename

    def getItem(self,item_data):
        url = self.baseurl + item_data['add_to_cart_link']
        response = self.session.get(url)
        parsed_json = json.loads(response.text)
        parsed_html = BeautifulSoup(parsed_json['message'],'html.parser')
        for atag in parsed_html.find_all("a"):
            url= atag.get("href")
            if url.find("downloadepub")>0 and self.epub == True:
                self.downloadFile(url,item_data['author'] + " - " + item_data['title']+'.epub')
            if url.find("downloadmobi")>0 and self.mobi == True:
                self.downloadFile(url,item_data['author'] + " - " + item_data['title']+'.mobi')


##### 

def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def main(argv):
    username = ''
    password = ''
    mobi = False
    epub = False
    directory = "woblink"

    parser = argparse.ArgumentParser(description='Script for downloading free ebooks from woblink.com')
    parser.add_argument('-user', type=str, dest="username",  required=True,
                    help='Username for Woblink.com')
    parser.add_argument('-pass', type=str, dest="password",  required=True,
                    help='Password for Woblink.com')
    parser.add_argument('-dir', type=str, dest="directory", default="woblink",
                    help='Directory for download. Default: woblink')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--epub', action="store_true",
                    help='Download EPUB. Default: false')
    group.add_argument('--mobi', action="store_true",
                    help='Download MOBI. Default: false')


    args = parser.parse_args()
    username = args.username
    password = args.password
    epub = args.epub
    mobi = args.mobi
    directory = args.directory

    if username is None:
        username = input("Username: ")
    if password is None:
        password = getpass("Password: ")

    if mobi == False and epub == False:
        mobi = query_yes_no("Download MOBI?")
        epub = query_yes_no("Download EPUB?")

    if len(password) > 0 and len(username) >0 and (mobi == True or epub == True):
        try:
            os.makedirs(directory)
        except OSError:
            pass
        obj = Woblink(username,password,epub,mobi,directory)
        obj.login()
        obj.getBooks()
        obj.logout

    else:
        sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])