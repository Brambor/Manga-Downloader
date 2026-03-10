import download_abstract
import html_to_url

url = "https://dandadanmanga.org/"
url_chapter_common = f"{url}manga/"
folder = "DanDaDan"

def img_srcs_from_page(webpage_read):
	# some chapters (from 188) use different html in <img>
	break1 = 'aligncenter" src="'
	break2 = 'async" src="'
	before_src = break1 if break1 in webpage_read else break2

	parts = webpage_read.split(before_src)[1:]
	pic_urls = tuple(p.split('"')[0] for p in parts)
	return pic_urls

download_abstract.program(
	url,
	folder,
	html_to_url.chapter_to_urls_generator(url_chapter_common),
	html_to_url.url_to_chapter_name,
	img_srcs_from_page
)
