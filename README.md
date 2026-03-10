# Manga-Downloader
Download manga from the chosen website into sensible folders. Then create a `.pdf` file out of them.

## To download manga

1. Either use provided `download_impl_*.py` or write a new one. We will use `download_impl_DanDaDan.py` as
an example.
2. Launch `download_impl_DanDaDan.py`, it will download pictures of manga into `download/DanDaDan`,
one folder per chapter, one picture per panel.
3. Note: You can stop the download and launch it later to come back to it or to download new chapters.
It will not redownload pictures, but if any are missing, it will download them.
You can delete pictures or whole folders if something is wrong and redownload them.
4. Sometimes a few panels don't get downloaded, and the program waits infinitely. Try killing it
(Ctrl+C works) and launching it again. As per step 3, only missing pictures will be downloaded.
5. If any panels or chapters don't download, an `.error` file is hardlinked in their place to make sure
the reader knows. The `.error` files will be removed automatically if the download succeeds on another
`download_impl_DanDaDan.py` launch.

## To create a `.pdf` from downloaded images

1. Edit `create_pdf.py` at the top to select the folder from which to create `.pdf`,
e.g. `folder = "DanDaDan"`.
2. Launch `create_pdf.py`.
3. It will create `partial_pdf/DanDaDan` folder, and in there it will create or overwrite `.pdf` files
containing up to `batch` panels each (100 by default).
Note: Python consumes too much memory when done in one swoop (watching the RAM usage is fun).
4. Then it will read (only the) created `.pdf` files and compose them into one gigantic `.pdf` file
at `pdf/DanDaDan.pdf`.
5. After finishing, the `partial_pdf` folder can be safely deleted.
Even if left untouched, it will not be reused.
