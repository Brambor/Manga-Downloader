import download_abstract
import html_to_url

url = "https://www.frieren.online/"
url_chapter_common = "https://ww2.frieren.online/manga/"
folder = "frieren"
ignore_chapters = {
	"2-1",  # 002 = 002-1 + 002-2
	"2-2",  # 002 = 002-1 + 002-2
	"93-1",  # 093-1 = 093-5
	"98-1",  # 098-1 = 098-5
	"98-2",  # 098-2 = 098-5
}

def img_srcs_from_page(webpage_read):
	parts = webpage_read.split('" class="wp-manga-chapter-img')[:-1]
	pic_urls = tuple(p.split('src="')[-1].split("&")[0] for p in parts)
	return pic_urls

download_abstract.program(
	url,
	folder,
	html_to_url.chapter_to_urls_generator(url_chapter_common, ignore_chapters),
	html_to_url.url_to_chapter_name,
	img_srcs_from_page
)
