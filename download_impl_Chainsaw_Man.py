import download_abstract
import html_to_url

url = "https://chainsawmann.com/"
url_chapter_common = f"{url}manga/"
folder = "Chainsaw Man"

def img_srcs_from_page(webpage_read):
	# first pannel is there twice, so take just one
	parts = webpage_read.split('<meta property="og:image" content="')[2:]
	pic_urls = tuple(p.split('"')[0] for p in parts)
	return pic_urls

download_abstract.program(
	url,
	folder,
	html_to_url.chapter_to_urls_generator(url_chapter_common),
	html_to_url.url_to_chapter_name,
	img_srcs_from_page
)
