import download_abstract
import html_to_url

url = "https://dandadanmanga.net/"
url_chapter_common = "https://ww3.dandadanmanga.net/manga/"
folder = "DanDaDan"

def img_srcs_from_page(webpage_read):
	parts = webpage_read.split('" class="wp-manga-chapter-img')[:-1]
	pic_urls = tuple(p.split('src="')[-1].strip() for p in parts)
	return pic_urls

download_abstract.program(
	url,
	folder,
	html_to_url.chapter_to_urls_generator(url_chapter_common),
	html_to_url.url_to_chapter_name,
	img_srcs_from_page
)
