from urllib.request import Request, urlopen
import time
import os

def myrequest(url):
	worked = False
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	while not worked:
		try:
			webpage_read = urlopen(req).read()
			worked = True
		except:
			print("failed to connect to \n{}".format(url))
	return(webpage_read)

#input(url)
url = "http://www.mangahere.co/manga/mysterious_girlfriend_x" #base = "http://www.mangareader.net/mysterious-girlfriend-x/0/1"

#paths
folder = url.split("/")[-1]
path = "{}/{}/{}".format(os.getcwd(), "downloaded", folder) #"C:\\Users\\Tonda_2\\Desktop\\harddisk\\MGX"; "C:\Users\Tonda_2\Documents\GitHub\Manga-Downloader"
allpath = "{}/pics".format(path)
if not os.path.exists(allpath):
	os.makedirs(allpath)
path_urls = "{}/{}".format(path, "urls.txt")

if os.path.exists(path_urls):
	check = input("Wana check chapters? (write something for YES, enter for NO: ")
else:
	check = True
if check != "":
	print("Checking chapters...")
	start = time.time()

	webpage_read = myrequest(url).decode("utf-8")
	allpages = webpage_read.split('<div class="chapters_points clearfix">')[1].split('</ul><ul class="tab_comment clearfix">')[0]
	pages = allpages.split('href="')
	chapurl = [p.split('/"')[0] for p in pages if '/"' in p]

	chapurl_sorted = []
	tags = sorted([ch.split("/c")[1] for ch in chapurl])
	for i in range(len(chapurl)):
		for ch in sorted(chapurl):
			if tags[i] in ch:
				chapurl_sorted.append(ch)
				break

	urls_eps = []
	if os.path.exists(path_urls):
		urlfile = open(path_urls, "r")
		ufr = urlfile.read()
		urls_eps = ufr.split("\n") if ufr != "" else []
		urlfile.close()

	urls = [ue.split()[0] for ue in urls_eps]
	chaps_to_search = []
	for ch in chapurl_sorted:
		if ch not in urls:
			chaps_to_search.append(ch)

	for ch in chaps_to_search:
		ted = time.time()
		currentchap = ch.split("/")[-1]
		webpage_read = myrequest(ch).decode("utf-8")
		allepurl = webpage_read.split('onchange="change_page(this)">')[1].split("</select>")[0]
		there_are_x_ep = len(allepurl.split("{}/".format(currentchap))) - 1
		print("in chap {}\tare {} ep\t{}".format(float(currentchap[1:]) if "." in currentchap else int(currentchap[1:]), there_are_x_ep, time.time() - ted))
		urls_eps.append("{} {}".format(ch, there_are_x_ep))

		urlfile = open(path_urls, "w")
		urlfile.write("\n".join(urls_eps))
		urlfile.close()

	print("It took {} secs to check chapters".format(time.time() - start))



print("Downloading pics...")
start2 = time.time()


urlfile = open(path_urls, "r")
urls_eps = urlfile.read().split("\n") #http://www.mangahere.co/manga/mysterious_girlfriend_x/v01/c003 25
urlfile.close()

downloaded = [f.split(".")[0] for f in os.listdir("{}/pics".format(path))] #"E:/MGX/MGX pics"
celkem = 0

for url_ep in urls_eps:

	url, maxep = url_ep.split()
	maxep = int(maxep)
	chap = url.split("/")[-1][2:] #[1:]
	if "." in chap:
		chap = chap.replace(".", "")
	else:
		chap = "{}0".format(chap)

	for ep in range(1, maxep + 1):
		ted = time.time()
		name = "{}{}".format(chap, "{}{}".format((2 - len(str(ep))) * "0", ep))
		if name in downloaded:
			print("skipped {}".format(name))
			continue

		webpage_read = myrequest("{}/{}.html".format(url, ep))
		url_to_pic = webpage_read.decode("utf-8").split('" onerror="')[0].split('<img src="')[-1]

		pic = myrequest(url_to_pic)

		myfile = open("{}/pics/{}.jpg".format(path, name), "wb")
		myfile.write(pic)
		myfile.close()
		celkem += 1

		print("strana {}\tza {}\tsekund".format(name, time.time() - ted))
		#myfile = open("{}\{}.jpg".format("{}\\{}".format(path, "MGX pics"), petinazev), "wb")

print("{} stranek\tza {}\tsekund".format(celkem, time.time() - start2))

input("DONE")
