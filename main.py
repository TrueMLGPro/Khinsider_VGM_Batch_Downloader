from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from functools import partial
import os
import re

from downloader.utils.metadata import get_album_name, get_album_metadata
from downloader.ui.widgets import *

import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen

from rich import print as rprint
from rich import traceback as rich_traceback
from rich.live import Live
from rich.progress import Progress, TaskID

page_html = ""
tasks = []

class Task:
	def __init__(self, name, url):
		self.name = name
		self.url = url

def get_html_content(url: str):
	response = requests.get(url)
	response.raise_for_status()
	return BeautifulSoup(response.text, features="html.parser")

def get_full_metadata(html: BeautifulSoup):
	album_metadata: dict = {"album_name": get_album_name(html), **get_album_metadata(html)}
	return album_metadata

def print_metadata(full_metadata: dict):
	rprint(f"[green bold]Album Name:[/] [bright_cyan]{full_metadata['album_name']}[/]")
	rprint(f"[green bold]Platforms:[/] [bright_cyan]{full_metadata['platforms']}[/]")
	rprint(f"[green bold]Year:[/] [bright_cyan]{full_metadata['year']}[/]")
	rprint(f"[green bold]Developed by:[/] [bright_cyan]{full_metadata['developed_by']}[/]")
	rprint(f"[green bold]Published by:[/] [bright_cyan]{full_metadata['published_by']}[/]")
	rprint(f"[green bold]Tracks:[/] [bright_cyan]{full_metadata['number_of_files']}[/]")
	rprint(f"[green bold]Total Album Size:[/] [bright_cyan]{full_metadata['total_filesize']}[/]")
	rprint(f"[green bold]Date Added:[/] [bright_cyan]{full_metadata['date_added']}[/]")
	rprint(f"[green bold]Uploaded by:[/] [bright_cyan]{full_metadata['uploaded_by']}[/]")

	if full_metadata["changelog"] != "-":
		rprint("[green bold]Changelog:[/green bold]")
		for changelog_item in full_metadata['changelog']:
			date, change = changelog_item.split(":")
			rprint(f"[blue bold] - {date}[/]: [bright_cyan]{change.strip()}[/]")

def get_song_data(html: BeautifulSoup):
	"""
	Get the album name from the Khinsider album HTML content.
	"""
	table = html.find("table", id="songlist")
	song_data_list = []

	for row in table.findAll("tr")[1:-1]:
		try:
			song_name_element = row.find("td", class_="clickable-row")
			link_element = row.findAll("a")[0]

			if song_name_element:
				song_name: str = song_name_element.text.strip()
				href = link_element['href']
				song_link: str = 'https://downloads.khinsider.com' + href if href.startswith('/') else href

				# Create dictionary and add to the list
				song_data: dict = {'song_name': song_name + ".mp3", 'song_link': song_link} # TODO: REMAKE THIS TO USE A FORMAT GRABBED FROM THE URL (MP3, FLAC, etc.)
				song_data_list.append(song_data)

		except Exception as e:
			print(f"Error extracting song data: {e}")
			print(row)

	return song_data_list

def get_track_download_link(url: str):
	"""
	Get the download link for the track.
	"""
	response = requests.get(url)
	response.raise_for_status()
	html = BeautifulSoup(response.text, features="html.parser")
	audio = html.find("audio")

	return audio["src"]

def download_song(url: str, filename: str, album_folder: str, task_progress_bar: Progress):
	"""
	Download the song from the given URL and save it with the specified filename.
	"""
	download_path = os.path.join(album_folder, filename)

	if os.path.exists(download_path):
		rprint(f"File '{filename}' exists, skipping.")
		return

	response = urlopen(url)

	# Convert the file size from bytes to megabytes
	file_size = int(response.info()["Content-Length"])
	# file_size_mb: float = float(file_size) / 1000000

	# Start the download
	with open(download_path, "wb") as file:
		task = task_progress_bar.add_task(f"[cyan]{filename}", total=file_size)
		for data in iter(partial(response.read, 32768), b""):
			file.write(data)
			task_progress_bar.update(task, advance=len(data))

	return filename

def start_downloads(album_folder: str, download_tasks: list[Task], overall_task_id: TaskID):
	# Create a multi-threaded Live instance
	with Live(OUTER_PANEL, refresh_per_second=8, vertical_overflow=ELLIPSIS):
		with ThreadPoolExecutor(max_workers=4) as pool:
			# Download songs using executor.submit and as_completed
			futures: list[Future] = [pool.submit(download_song, get_track_download_link(task.url), task.name, album_folder, TASK_PROGRESS_BAR) for task in download_tasks]

			# Wait for all tasks to complete
			for _ in as_completed(futures):
				try:
					OVERALL_PROGRESS_BAR.advance(overall_task_id, advance=1)
				except Exception as e:
					print(e)

def main():
	album_url: str = input("Input a link for the Khinsider album: ")
	page_html: BeautifulSoup = get_html_content(album_url)
	full_metadata: list = get_full_metadata(page_html)
	print_metadata(full_metadata)

	# Create a folder for the album
	album_folder: str = os.path.join(os.getcwd(), re.sub(r'[\/:*?"<>|]', '', full_metadata['album_name']))
	os.makedirs(album_folder, exist_ok=True)

	# Get song data of every song
	song_data_list = get_song_data(page_html)
	song_names: list = [song['song_name'] for song in song_data_list]
	song_links: list = [song['song_link'] for song in song_data_list]

	song_count: int = len(song_links)
	rprint(f"[blue bold]Got {song_count} links![/]")

	download_tasks = [Task(name=f"{song_num}. {song_name}", url=song_link) for song_num, song_name, song_link in zip(range(1, len(song_names)), song_names, song_links)]
	overall_task_id = OVERALL_PROGRESS_BAR.add_task("[green]Processing[/]", total=len(download_tasks))

	# Start the downloader
	start_downloads(album_folder, download_tasks, overall_task_id)

	rprint(f"Downloaded {song_count} files to '{album_folder}'!")

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		exception_type = type(e)
		tb_obj = e.__traceback__
		exc_tb = e.with_traceback(tb_obj)
		rprint(rich_traceback.Traceback.from_exception(exc_type=exception_type, exc_value=e, traceback=tb_obj))
	except KeyboardInterrupt:
		rprint("\n🚀 [bold blue]Exiting...[/]")
