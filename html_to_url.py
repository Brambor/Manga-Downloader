from urllib.parse import urljoin

def url_to_chapter_name(chapter_url, i_start):
	chapter = chapter_url[i_start:]
	if "-" in chapter:
		x, y = chapter.split("-")
		y = f"-{y}"
	else:
		x = chapter
		y = ""
	return x.zfill(3)+y

def equal_until(chapter_urls):
	# INDEX UNTIL which all chapter_urls are equal
	i = -1
	while True:
		i += 1
		if i >= len(chapter_urls[0]):
			return i
		char = chapter_urls[0][i]
		for chap in chapter_urls:
			if i >= len(chap) or chap[i] != char:
				return i

def manga_sort_generator(i_start):
	def manga_sort(chapter_url):
		chapter = chapter_url[i_start:]
		if "-" in chapter:
			x, y = chapter.split("-")
			return int(x)*10 + int(y)
		return int(chapter)*10
	return manga_sort

def chapter_to_urls_generator(url_chapter_common):
	def chapters_html_to_chapter_urls(all_chapters_html):
		# set to remove duplicities
		chapter_urls = set(p.split("/")[0] for p in all_chapters_html.split(url_chapter_common)[1:])
		chapter_urls = [urljoin(url_chapter_common, ch) for ch in chapter_urls]
		# sort
		return sorted(chapter_urls, key=manga_sort_generator(equal_until(chapter_urls)))
	return chapters_html_to_chapter_urls
