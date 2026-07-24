import download_abstract
import html_to_url

url = "https://w6.villains-destined.online/"
url_chapter_common = f"{url}comic/"
folder = "Villains Are Destined to Die"

def img_srcs_from_page(webpage_read):
	parts = webpage_read.split("lazyload src='")[1:]
	pic_urls = tuple(p.split("'")[0] for p in parts)
	return pic_urls

download_abstract.program(
	url,
	folder,
	html_to_url.chapter_to_urls_generator(url_chapter_common),
	html_to_url.url_to_chapter_name,
	img_srcs_from_page
)
