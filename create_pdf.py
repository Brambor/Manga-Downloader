import os
from PIL import Image
from time import time
from math import ceil
from pypdf import PdfWriter

#folder = "frieren"
folder = "DanDaDan"
#folder = "Chainsaw Man"
#folder = "Yamada to lvl 999"
batch = 100

def get_rgb_img(file):
	img = Image.open(file)
	img.load()
	# If RGBA image, convert it to RGB image.
	if (len(img.split()) == 4):
		background = Image.new("RGB", img.size, (255, 255, 255))
		background.paste(img, mask=img.split()[3]) # 3 is the alpha channel
		img = background
	return img

def generator(file_paths):
	for i, file in enumerate(file_paths):
		yield get_rgb_img(file)

def now(since_t):
	return f"{time()-since_t:6.2f} sec:"

t0 = time()

print(f"{now(t0)} start")
print(f"{now(t0)} will create pdf from {folder}")

path = "{}/{}/{}".format(os.getcwd(), "downloaded", folder)

file_paths = []
for chapter in os.listdir(path):
	for file in os.listdir(f"{path}/{chapter}"):
		file_paths.append(f"{path}/{chapter}/{file}")
print(f"{now(t0)} listed {len(file_paths)} file_paths")

partial_pdf_folder = "{}/partial_pdf/{}".format(os.getcwd(), folder)
partial_pdf_paths = []
# CREATE PARTIAL PDFS WITH `batch` pages each
for i in range(ceil(len(file_paths)/batch)):
	first = i*batch
	last = min((i+1)*batch, len(file_paths))  # non inclusive
	partial_pdf_path = "{}/{}".format(partial_pdf_folder, f"{folder}_from_{first}_to_{last-1}.pdf")
	if not os.path.exists(partial_pdf_folder):
		os.makedirs(partial_pdf_folder)
	get_rgb_img(file_paths[first]).save(
		partial_pdf_path, "PDF", resolution=100.0, save_all=True,
		append_images=generator(file_paths[first+1:last])
	)
	print(f"{now(t0)} saved pdf {partial_pdf_path}")
	partial_pdf_paths.append(partial_pdf_path)

pdf_folder = "{}/{}".format(os.getcwd(), "pdf")
pdf_path = "{}/{}".format(pdf_folder, f"{folder}.pdf")
merger = PdfWriter()
for i, pdf in enumerate(partial_pdf_paths):
	print(f"{now(t0)} merging pdfs: {i+1}/{len(partial_pdf_paths)}")
	merger.append(pdf)

print(f"{now(t0)} writing final pdf")

if not os.path.exists(pdf_folder):
	os.makedirs(pdf_folder)
merger.write(pdf_path)

print(f"{now(t0)} finished {pdf_path}")
