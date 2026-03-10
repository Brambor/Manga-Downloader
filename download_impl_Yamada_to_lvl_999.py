from urllib.parse import urljoin

import download_abstract
import html_to_url

url = "https://www.mgeko.cc/manga/yamada-kun-to-lv999-no-koi-wo-suru/all-chapters/"
url_chapter_common = "https://www.mgeko.cc/reader/en/"
url_pic_starts_with = "/reader/en/"
folder = "Yamada to lvl 999"

# custom: addded url_pic_starts_with
def custom_chapter_to_urls_generator(url_chapter_common, url_pic_starts_with):
	def sort_generator(i_start):
		def custom_sort(url):
			return int(url[i_start:].split("-")[0])
		return custom_sort

	def chapters_html_to_chapter_urls(all_chapters_html):
		# set to remove duplicities
		chapter_urls = set(p.split("/")[0] for p in all_chapters_html.split(url_pic_starts_with)[1:])
		chapter_urls = [urljoin(url_chapter_common, ch) for ch in chapter_urls]
		# sort
		return sorted(chapter_urls, key=sort_generator(html_to_url.equal_until(chapter_urls)))
	return chapters_html_to_chapter_urls

def custom_url_to_chapter_name(chapter_url, i_start):
	return chapter_url[i_start:].split("-")[0].zfill(3)

def img_srcs_from_page(webpage_read):
	# :-2 to exclude credits.jpg at the end
	parts = webpage_read.split('" onerror="tryAgain(this)')[:-2]
	pic_urls = tuple(p.split('"')[-1] for p in parts)
	return pic_urls

download_abstract.program(
	url,
	folder,
	custom_chapter_to_urls_generator(url_chapter_common, url_pic_starts_with),
	custom_url_to_chapter_name,
	img_srcs_from_page
)
