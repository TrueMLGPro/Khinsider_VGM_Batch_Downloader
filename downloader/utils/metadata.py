from bs4 import BeautifulSoup
import re
from rich import print as rprint

def get_album_name(html: BeautifulSoup):
	"""
	Get the album name from the Khinsider album URL.
	"""
	album_name = html.find("h2")

	# Check if <h2> tag is found and has contents
	if album_name and album_name.contents:
		# Filter out non-string elements and join the strings
		album_name = ' '.join(str(child) for child in album_name.contents if isinstance(child, str))
		return album_name.strip()
	return None

def get_album_metadata(html: BeautifulSoup):
	"""
	Get the album metadata from the Khinsider album URL.
	"""
	metadata = {}
	p_tag = html.find("p", align="left")

	# Extract album description
	if p_tag:
		lines = p_tag.stripped_strings
		key = None

		for line in lines:
			if ":" in line:
				key, value = map(str.strip, line.split(":", 1))
				formatted_key = key.lower().replace(" ", "_")

				if formatted_key == 'date_added':
					date_added_match = re.search(r'Date Added:\s*<b>(.*?)</b>', str(html))
					if date_added_match:
						metadata['date_added'] = date_added_match.group(1)
					else:
						metadata['date_added'] = ''
					# Remove content after date_added until the end of the p tag
					break
				else:
					metadata[formatted_key] = value
			elif key:
				metadata[formatted_key] += re.sub(r',\s*', ', ', line)

		# Extract changelog
		changelog_element = html.find("a", class_="change_log_dropdown")
		if changelog_element:
			tooltip_span = changelog_element.find_next("span", class_="tooltip")
			if tooltip_span:
				changelog_items = [item for item in tooltip_span.stripped_strings]
				metadata["changelog"] = changelog_items
		else:
			metadata["changelog"] = "-"

		# Extract uploader
		uploader_element = html.find("a", href=re.compile(r'/forums/index.php\?members/\d+/'))
		if uploader_element:
			metadata['uploaded_by'] = uploader_element.text.strip()

	return metadata

# rprint(get_album_metadata("https://downloads.khinsider.com/game-soundtracks/album/super-mario-world-snes-gamerip"))