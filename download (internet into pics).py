from urllib.request import Request, urlopen
import time
import os
import _thread

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
	check = input("Wana check chapters? (write something for YES, enter for NO): ")
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
		with open(path_urls, "r") as urlfile:
			urls_eps = urlfile.read().split("\n")
			if urls_eps[0] == "":
				del urls_eps[0]
				with open(path_urls, "w") as urlfile:
					urlfile.write("\n".join(urls_eps))



	urls = [ue.split()[0] for ue in urls_eps]
	chaps_to_search = chapurl_sorted

	for u in urls:
		if u in chapurl_sorted:
			del chapurl_sorted[chapurl_sorted.index(u)]


	def thrue_thread_download_pages(ch, path_urls):
		global finished
		ted = time.time()
		currentchap = ch.split("/")[-1]
		webpage_read = myrequest(ch).decode("utf-8")
		allepurl = webpage_read.split('onchange="change_page(this)">')[1].split("</select>")[0]
		there_are_x_ep = len(allepurl.split("{}/".format(currentchap))) - 1
		#print("in chap {}\tare {} ep\t{}".format(float(currentchap[1:]) if "." in currentchap else int(currentchap[1:]), there_are_x_ep, time.time() - ted))
		urls_eps.append("\n{} {}".format(ch, there_are_x_ep))
		addhere = "\n{} {}".format(ch, there_are_x_ep)


		with open(path_urls, "a") as urlfile:
			urlfile.write(addhere)
		finished += 1
	finished = 0
	for ch in chaps_to_search:
		_thread.start_new_thread(thrue_thread_download_pages, (ch, path_urls))

	#print("It took {} secs to check chapters".format(time.time() - start))
	
	checker = -1
	goal = len(chaps_to_search)
	while finished != goal:
		if finished != checker:
			checker = finished
			print("{} of {} checked".format(finished, goal))
		time.sleep(0.1)


print("Downloading pics...")
start2 = time.time()


urlfile = open(path_urls, "r")
urls_eps = urlfile.read().split("\n") #http://www.mangahere.co/manga/mysterious_girlfriend_x/v01/c003 25
urlfile.close()

downloaded = [f.split(".")[0] for f in os.listdir("{}/pics".format(path))] #"E:/MGX/MGX pics"
celkem = 0

goal = 0
finished = 0
lock = _thread.allocate_lock()
def thrue_thread_download_pics(path, url, ep, name):
	lock.acquire()
	global goal
	goal += 1
	lock.release()
	webpage_read = myrequest("{}/{}.html".format(url, ep))
	url_to_pic = webpage_read.decode("utf-8").split('" onerror="')[0].split('<img src="')[-1]

	pic = myrequest(url_to_pic)

	myfile = open("{}/pics/{}.jpg".format(path, name), "wb")
	myfile.write(pic)
	myfile.close()
	global finished
	finished += 1


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
			#print("skipped {}".format(name))
			continue

		###
		_thread.start_new_thread(thrue_thread_download_pics, (path, url, ep, name))
		###
		#print("strana {}\tza {}\tsekund".format(name, time.time() - ted))

checker = -1
while finished != goal:
	if finished != checker:
		checker = finished
		print("{} of {} downloaded".format(finished, goal))
	time.sleep(0.1)

print("{} stranek\tza {}\tsekund".format(celkem, time.time() - start2))

input("DONE")
