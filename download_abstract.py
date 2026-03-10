import os
import queue
import signal
import threading

from datetime import datetime
from math import ceil
from urllib.request import Request, urlopen

from progress import ProgressRectangles
import html_to_url

# allow quit with ctrl+C
signal.signal(signal.SIGINT, signal.SIG_DFL)

lock = threading.Lock()

def myrequest(url):
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	tries_left = 10
	while tries_left > 0:
		try:
			return urlopen(req).read()
		except:
			tries_left -= 1
	return None

#q_chapter_url items: (i_chapter, chapter_url)
def worker_get_urls(path, i_start, fnc_img_srcs_from_page, fnc_url_to_chapter_name,
	q_chapter_url, q_pic_url, q_finished
):
	"""
	worker thread for scraping image urls from (requesting) the chapter url
	"""
	while True:
		i_chapter, chapter_url = q_chapter_url.get()

		webpage_read = myrequest(chapter_url).decode("utf-8")

		pic_urls = fnc_img_srcs_from_page(webpage_read)

		# DOWNLOAD ALL PICS OF CHAPTER

		goal = len(pic_urls)

		folder = f"{path}/{fnc_url_to_chapter_name(chapter_url, i_start)}"
		if not os.path.exists(folder):
			os.makedirs(folder)
		for i_panel, pic_url in enumerate(pic_urls):
			pic_format = pic_url.split(".")[-1]
			file_path = f"{folder}/{str(i_panel).zfill(3)}.{pic_format}"
			if os.path.exists(file_path):
				# asume we already downloaded this file
				# chapter isn't finished, just one panel of it
				q_finished.put((i_chapter, goal, +1, 0))
				continue
			q_pic_url.put((pic_url, file_path, i_chapter, goal))
		error_file_path = f"{folder}/chapter_error.png"
		if pic_urls:
			# show we fetched the chapter
			q_finished.put((i_chapter, goal, 0, 0))
			# remove error file
			if os.path.exists(error_file_path):
				os.remove(error_file_path)
		else:
			q_finished.put((i_chapter, 0, +1, +1))
			# add error file
			if not os.path.exists(error_file_path):
				os.link("resources/FAILED_chapter.png", error_file_path)

		q_chapter_url.task_done()

def worker_download_pics(q_pic_url, q_finished):
	"""
	worker thread for downloading individual image from (requesting) the image url
	"""
	while True:
		pic_url, file_path, i_chapter, goal = q_pic_url.get()
		error_file_path = file_path + ".error"

		pic = myrequest(pic_url)
		if pic == None:
			if not os.path.exists(error_file_path):
				os.link("resources/FAILED_pannel.png", error_file_path)
			q_finished.put((i_chapter, goal, +1, +1))
			q_pic_url.task_done()
			continue
		with open(file_path, "wb") as myfile:
			myfile.write(pic)
		if os.path.exists(error_file_path):
			os.remove(error_file_path)

		# chapter isn't finished, just one panel of it
		q_finished.put((i_chapter, goal, +1, 0))

		q_pic_url.task_done()

def worker_UI(goal, q_finished, chapter_names, PR):
	"""
	worker for updating UI showing progress, only single instance shall be run
	"""
	PR.reset_n_entries(goal)
	finished_list = [0    for _ in range(goal)]
	goal_list     = [None for _ in range(goal)]
	failed_list   = [0    for _ in range(goal)]
	while True:
		# update all waiting data
		while not q_finished.empty():
			i_chapter, goal, finished, failed = q_finished.get()
			failed_list[i_chapter] += failed
			if failed:
				with lock:
					PR.print_message(f"FAILED chapter: {chapter_names[i_chapter]}, {i_chapter}-th in-order")

			finished_list[i_chapter] += finished
			goal_list[i_chapter] = goal

			q_finished.task_done()
		# print data
		with lock:
			PR.print_data(finished_list, goal_list, failed_list, chapter_names)

# PROGRAM
def program(
	url,
	folder,
	fnc_chapters_html_to_chapter_urls,
	fnc_url_to_chapter_name,
	fnc_img_srcs_from_page,
):
	"""
	request the url to get individual chapters,
	pass those to worker threads who get image urls,
	pass those to another worker threads who download the images

	run worker to update UI displaying the progress
	"""
	path = "{}/{}/{}".format(os.getcwd(), "downloaded", folder)

	PR = ProgressRectangles(1)
	PR.print_message(f"\n\n----------\nstarted downloading {folder}")
	PR.print_message(datetime.now())
	PR.print_data([0], [None], [0], ["name"])

	# GET CHAPTER URLS
	page_object = myrequest(url)
	if page_object == None:
		PR.print_message("url invalid / not connected to internet")
		return
	all_chapters_html = page_object.decode("utf-8")

	chapter_urls = fnc_chapters_html_to_chapter_urls(all_chapters_html)
	i_start = html_to_url.equal_until(chapter_urls)

	# PARAMETERS
	# n of workers downloading the images
	workers_get_pic = 100
	# n of workers scraping image urls from each chapter
	worker_get_pic_url = ceil(workers_get_pic / 18)
	# max n of stored image urls before url scrapers wait
	queue_max_stash = workers_get_pic * 5 // 4

	# DOWNLOAD
	q_chapter_url = queue.Queue()
	q_pic_url = queue.Queue(queue_max_stash)
	q_finished = queue.Queue()

	# Turn-on the url getting worker threads.
	for i in range(worker_get_pic_url):
		threading.Thread(
			target=worker_get_urls,
			args=(path, i_start, fnc_img_srcs_from_page, fnc_url_to_chapter_name,
				q_chapter_url, q_pic_url, q_finished),
			daemon=True
		).start()
	# Turn-on the picture getting worker threads.
	for i in range(workers_get_pic):
		threading.Thread(
			target=worker_download_pics,
			args=(q_pic_url, q_finished),
			daemon=True
		).start()

	# A single printing thread.
	names = tuple(fnc_url_to_chapter_name(chapter_url, i_start) for chapter_url in chapter_urls)
	threading.Thread(
		target=worker_UI,
		args=(len(chapter_urls), q_finished, names, PR),
		daemon=True
	).start()

	# initial batch
	for i_chapter, chapter_url in enumerate(chapter_urls):
		q_chapter_url.put((i_chapter, chapter_url))

	# wait until all jobs are done
	q_chapter_url.join()
	q_pic_url.join()
	q_finished.join()
	with lock:
		PR.print_message('finished')
		PR.print_message(datetime.now())
		PR.print_last_data()
