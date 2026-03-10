import colorama
import os
import sys

from datetime import datetime
from math import ceil

from show_hide_cursor import show_cursor, hide_cursor

colorama.init()

"""
Print progress in the following way:
1. get terminal size, always adhere to it's size
2. make equal rectangle for each entry
3. The rectangle contains:
	|121-2| Entry name
	|12/20| Real progress
	|60%  | Computed progress. OR chapters failed |3 FAIL|
4. Colors:
	Blue - unknown
	White - unstarted
	Yellow - in progress
	Green - finished
	Red - failed
"""

class ProgressRectangles():
	def __init__(self, n_entries):
		self.printed_data_lines = 0
		self.n_entries = None
		self.last_finished = []
		self.last_goal = []
		self.last_failed = []
		self.last_names = []
		self.last_ter_size = None
		self.last_n_entries = None
		self.reset_n_entries(n_entries)

	def reset_n_entries(self, n_entries):
		force_recalculate = self.n_entries != n_entries
		self.n_entries = n_entries

		# choose mode so it fits
		self.choose_mode(force_recalculate)

	def print_how_much_fits(self, ter_size):
		per_line = self.fit_in(ter_size[0], self.rectangle_width)
		if self.compact_mode:
			per_column = ter_size[1]
		else:
			per_column = self.fit_in(ter_size[1], self.rectangle_height)
		total = per_line * per_column

		self.print_message(f"compact: {self.compact_mode} can fit horizontally: {per_line}; "
			f"vertically: {per_column}; total: {total}; entries {self.n_entries}")

	def choose_mode(self, force_recalculate=False):
		ter_size = os.get_terminal_size()
		if not force_recalculate and self.last_ter_size == ter_size:
			return

		# normal mode
		self.n_width = 2
		self.rectangle_width = self.n_width * 2 + 1
		self.rectangle_height = 3

		per_line = self.fit_in(ter_size[0], self.rectangle_width)
		per_column = self.fit_in(ter_size[1], self.rectangle_height)
		total = per_line * per_column
		# it fits
		if total >= self.n_entries:
			self.compact_mode = False
			self.print_how_much_fits(ter_size)
			self.last_ter_size = ter_size
			self.last_n_entries = self.n_entries
			return

		# compact mode
		self.compact_mode = True
		self.n_width = None
		self.rectangle_width = 5
		self.rectangle_height = 1

		self.print_how_much_fits(ter_size)
		self.last_ter_size = ter_size
		self.last_n_entries = self.n_entries

	def clear_data_lines(self):
		print(colorama.ansi.clear_line(), end="")
		for _ in range(self.printed_data_lines):
			print(colorama.Cursor.UP(), end="")
			print(colorama.ansi.clear_line(), end="")
		self.printed_data_lines = 0

	def print_message(self, msg):
		self.clear_data_lines()
		print(msg)
		with open("download_log.txt", "a") as file:
			file.write(f"{datetime.now()}: {msg}\n")

	def print_last_data(self):
		self.print_data(self.last_finished, self.last_goal, self.last_failed, self.last_names)

	def print_data(self, finished, goal, failed, chapter_names):
		self.choose_mode()
		hide_cursor()
		ter_size = os.get_terminal_size()
		per_line = self.fit_in(ter_size[0], self.rectangle_width)
		# fits_perfectly meaning \n should not be printed
		fits_perfectly = self.fits_perfectly(ter_size[0], self.rectangle_width)

		per_column = self.fit_in(ter_size[1], self.rectangle_height)
		colors = tuple(self.cell_color(finished[i], goal[i], failed[i]) for i in range(self.n_entries))

		# move cursor up and overwrite rather than delete to lessen flickering
		for _ in range(self.printed_data_lines):
			print(colorama.Cursor.UP(), end="")
		self.printed_data_lines = 0

		for row in range(ceil(self.n_entries / per_line)):
			row_indexes = tuple(self.indexes(row, per_line))
			if len(row_indexes) == per_line and fits_perfectly:
				end = ""
			else:
				end = "\n"

			print(" ".join(colors[i]
					+f"{chapter_names[i][:5]:>{self.rectangle_width}}"
					+colorama.Style.RESET_ALL
				for i in row_indexes), end=end)

			if self.compact_mode:
				self.printed_data_lines += 1
				continue

			print(" ".join(colors[i]
					+f"{finished[i]:{self.n_width}}/"
						+(f"{'?':>{self.n_width}}" if goal[i] == None else f"{goal[i]:{self.n_width}}")
					+colorama.Style.RESET_ALL
				for i in row_indexes), end=end)

			print(" ".join(colors[i]
					+(f"{failed[i]:{self.rectangle_width-5}} FAIL"[:self.rectangle_width]
						if failed[i] else (
							f"{int(100*finished[i]/goal[i]):{self.rectangle_width-1}}%"
							if goal[i]
							else '?'*self.rectangle_width))
					+colorama.Style.RESET_ALL
				for i in row_indexes), end=end)
			print()
			self.printed_data_lines += 4
		self.last_finished = finished
		self.last_goal = goal
		self.last_failed = failed
		self.last_names = chapter_names
		show_cursor()

	def indexes(self, row, per_line):
		start = per_line * row
		end = min(start + per_line, self.n_entries)
		for i in range(start, end):
			yield i

	# NOT self.rectangle_width
	def fit_in(self, total_width, rectangle_width):
		if total_width < rectangle_width:
			return 0
		return 1 + (total_width-rectangle_width) // (rectangle_width+1)

	def fits_perfectly(self, total_width, rectangle_width):
		if total_width == rectangle_width:
			return True
		per_line = self.fit_in(total_width, rectangle_width)
		return per_line * (rectangle_width + 1) - 1 == total_width

	def cell_color(self, finished, goal, failed):
		if failed != 0:
			return colorama.Fore.RED
		elif goal == None:
			return colorama.Fore.BLUE
		elif finished == 0 and goal != 0:
			return ""  # white
		elif finished == goal:
			return colorama.Fore.GREEN
		return colorama.Fore.YELLOW

if __name__ == "__main__":
	# import time
	# dummy finished and goal
	print(os.get_terminal_size())

	entries = 1000
	finished = [0       for _ in range(entries)]
	goal     = [None    for _ in range(entries)]
	failed   = [0       for _ in range(entries)]
	names    = [f"{i}{i}." for i in range(entries)]

	PR = ProgressRectangles(entries)

	PR.print_data(finished, goal, failed, names)
	#time.sleep(1)

	goal[0] = 10
	finished[0] = 0
	PR.print_data(finished, goal, failed, names)
	#time.sleep(1)
	PR.print_message("TEST hi there")

	goal[3] = 10
	finished[3] = 3
	failed[3] = 5
	PR.print_data(finished, goal, failed, names)

	PR.reset_n_entries(50)

	PR.print_message("TEST failed to connect to\nhttps://dandadanmanga.org/manga/dandadan-chapter-180")
	PR.print_message("TEST failed to connect to\nhttps://dandadanmanga.org/manga/dandadan-chapter-180")
	PR.print_message("TEST failed to connect to\nhttps://dandadanmanga.org/manga/dandadan-chapter-180")
	PR.print_message("TEST failed to connect to\nhttps://dandadanmanga.org/manga/dandadan-chapter-180")

	goal[1] = 10
	finished[1] = 5
	PR.print_data(finished, goal, failed, names)
	#time.sleep(1)
	PR.print_message("TEST how are ya?\nlad?")

	goal[2] = 10

	for i in range(11):
		PR.reset_n_entries(i*10)
		finished[2] = i
		PR.print_data(finished, goal, failed, names)
	#time.sleep(1)

	PR.reset_n_entries(entries)
	goal[53] = 10
	finished[53] = 5
	PR.print_data(finished, goal, failed, names)
