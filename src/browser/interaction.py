#!/usr/bin/env python3
#
# natbot.py
# https://github.com/nat/natbot
#
# MODIFIED FOR DEVIKA

from playwright.sync_api import sync_playwright
import os
import time
from sys import exit, platform

from src.config import Config
from src.state import AgentState
from src.llm import LLM

prompt_template = """
You are an agent controlling a browser. You are given:

	(1) an objective that you are trying to achieve
	(2) the URL of your current web page
	(3) a simplified text description of what's visible in the browser window (more on that below)

You can issue these commands:
	SCROLL UP - scroll up one page
	SCROLL DOWN - scroll down one page
	CLICK X - click on a given element. You can only click on links, buttons, and inputs!
	TYPE X "TEXT" - type the specified text into the input with id X
	TYPESUBMIT X "TEXT" - same as TYPE above, except then it presses ENTER to submit the form

The format of the browser content is highly simplified; all formatting elements are stripped.
Interactive elements such as links, inputs, buttons are represented like this:

		<link id=1>text</link>
		<button id=2>text</button>
		<input id=3>text</input>

Images are rendered as their alt text like this:

		<img id=4 alt=""/>

Based on your given objective, issue whatever command you believe will get you closest to achieving your goal.
You always start on Google; you should submit a search query to Google that will take you to the best page for
achieving your objective. And then interact with that page to achieve your objective.

If you find yourself on Google and there are no search results displayed yet, you should probably issue a command 
like "TYPESUBMIT 7 "search query"" to get to a more useful page.

Then, if you find yourself on a Google search results page, you might issue the command "CLICK 24" to click
on the first link in the search results. (If your previous command was a TYPESUBMIT your next command should
probably be a CLICK.)

Don't try to interact with elements that you can't see.

Here are some examples:

EXAMPLE 1:
==================================================
CURRENT BROWSER CONTENT:
------------------
<link id=1>About</link>
<link id=2>Store</link>
<link id=3>Gmail</link>
<link id=4>Images</link>
<link id=5>(Google apps)</link>
<link id=6>Sign in</link>
<img id=7 alt="(Google)"/>
<input id=8 alt="Search"></input>
<button id=9>(Search by voice)</button>
<button id=10>(Google Search)</button>
<button id=11>(I'm Feeling Lucky)</button>
<link id=12>Advertising</link>
<link id=13>Business</link>
<link id=14>How Search works</link>
<link id=15>Carbon neutral since 2007</link>
<link id=16>Privacy</link>
<link id=17>Terms</link>
<text id=18>Settings</text>
------------------
OBJECTIVE: Find a 2 bedroom house for sale in Anchorage AK for under $750k
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT 8 "anchorage redfin"
==================================================

EXAMPLE 2:
==================================================
CURRENT BROWSER CONTENT:
------------------
<link id=1>About</link>
<link id=2>Store</link>
<link id=3>Gmail</link>
<link id=4>Images</link>
<link id=5>(Google apps)</link>
<link id=6>Sign in</link>
<img id=7 alt="(Google)"/>
<input id=8 alt="Search"></input>
<button id=9>(Search by voice)</button>
<button id=10>(Google Search)</button>
<button id=11>(I'm Feeling Lucky)</button>
<link id=12>Advertising</link>
<link id=13>Business</link>
<link id=14>How Search works</link>
<link id=15>Carbon neutral since 2007</link>
<link id=16>Privacy</link>
<link id=17>Terms</link>
<text id=18>Settings</text>
------------------
OBJECTIVE: Make a reservation for 4 at Dorsia at 8pm
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT 8 "dorsia nyc opentable"
==================================================

EXAMPLE 3:
==================================================
CURRENT BROWSER CONTENT:
------------------
<button id=1>For Businesses</button>
<button id=2>Mobile</button>
<button id=3>Help</button>
<button id=4 alt="Language Picker">EN</button>
<link id=5>OpenTable logo</link>
<button id=6 alt ="search">Search</button>
<text id=7>Find your table for any occasion</text>
<button id=8>(Date selector)</button>
<text id=9>Sep 28, 2022</text>
<text id=10>7:00 PM</text>
<text id=11>2 people</text>
<input id=12 alt="Location, Restaurant, or Cuisine"></input> 
<button id=13>Let's go</button>
<text id=14>It looks like you're in Peninsula. Not correct?</text> 
<button id=15>Get current location</button>
<button id=16>Next</button>
------------------
OBJECTIVE: Make a reservation for 4 for dinner at Dorsia in New York City at 8pm
CURRENT URL: https://www.opentable.com/
YOUR COMMAND: 
TYPESUBMIT 12 "dorsia new york city"
==================================================

The current browser content, objective, and current URL follow. Reply with your next command to the browser.

CURRENT BROWSER CONTENT:
------------------
$browser_content
------------------

OBJECTIVE: $objective
CURRENT URL: $url
PREVIOUS COMMAND: $previous_command
YOUR COMMAND:
"""

black_listed_elements = set(["html", "head", "title", "meta", "iframe", "body", "script", "style", "path", "svg", "br", "::marker",])

class Crawler:
	def __init__(self):
		self.browser = (
			sync_playwright()
			.start()
			.chromium.launch(
				headless=True,
			)
		)

		self.page = self.browser.new_page()
		self.page.set_viewport_size({"width": 1280, "height": 1080})
  
	def screenshot(self, project_name):
		screenshots_save_path = Config().get_screenshots_dir()

		page_metadata = self.page.evaluate("() => { return { url: document.location.href, title: document.title } }")
		page_url = page_metadata['url']
		random_filename = os.urandom(20).hex()
		filename_to_save = f"{random_filename}.png"
		path_to_save = os.path.join(screenshots_save_path, filename_to_save)

		self.page.emulate_media(media="screen")
		self.page.screenshot(path=path_to_save)

		new_state = AgentState().new_state()
		new_state["internal_monologue"] = "Browsing the web right now..."
		new_state["browser_session"]["url"] = page_url
		new_state["browser_session"]["screenshot"] = path_to_save
		AgentState().add_to_current_state(project_name, new_state)        

		return path_to_save

	def go_to_page(self, url):
		self.page.goto(url=url if "://" in url else "http://" + url)
		self.client = self.page.context.new_cdp_session(self.page)
		self.page_element_buffer = {}

	def scroll(self, direction):
		if direction == "up":
			self.page.evaluate(
				"(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop - window.innerHeight;"
			)
		elif direction == "down":
			self.page.evaluate(
				"(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop + window.innerHeight;"
			)

	def click(self, id):
		# Inject javascript into the page which removes the target= attribute from all links
		js = """
		links = document.getElementsByTagName("a");
		for (var i = 0; i < links.length; i++) {
			links[i].removeAttribute("target");
		}
		"""
		self.page.evaluate(js)

		element = self.page_element_buffer.get(int(id))
		if element:
			x = element.get("center_x")
			y = element.get("center_y")
			
			self.page.mouse.click(x, y)
		else:
			print("Could not find element")

	def type(self, id, text):
		self.click(id)
		self.page.keyboard.type(text)

	def enter(self):
		self.page.keyboard.press("Enter")

	def crawl(self):
		page = self.page
		page_element_buffer = self.page_element_buffer
		start = time.time()

		page_state_as_text = []

		device_pixel_ratio = page.evaluate("window.devicePixelRatio")
		if platform == "darwin" and device_pixel_ratio == 1:  # lies
			device_pixel_ratio = 2

		win_scroll_x 		= page.evaluate("window.scrollX")
		win_scroll_y 		= page.evaluate("window.scrollY")
		win_upper_bound 	= page.evaluate("window.pageYOffset")
		win_left_bound 		= page.evaluate("window.pageXOffset") 
		win_width 			= page.evaluate("window.screen.width")
		win_height 			= page.evaluate("window.screen.height")
		win_right_bound 	= win_left_bound + win_width
		win_lower_bound 	= win_upper_bound + win_height
		document_offset_height = page.evaluate("document.body.offsetHeight")
		document_scroll_height = page.evaluate("document.body.scrollHeight")

		# Removed unused percentage_progress variables

		tree = self.client.send(
			"DOMSnapshot.captureSnapshot",
			{"computedStyles": [], "includeDOMRects": True, "includePaintOrder": True},
		)
		strings	 	= tree["strings"]
		document 	= tree["documents"][0]
		nodes 		= document["nodes"]
		backend_node_id = nodes["backendNodeId"]
		attributes 	= nodes["attributes"]
		node_value 	= nodes["nodeValue"]
		parent 		= nodes["parentIndex"]
		node_types 	= nodes["nodeType"]
		node_names 	= nodes["nodeName"]
		is_clickable = set(nodes["isClickable"]["index"])

		text_value 			= nodes["textValue"]
		text_value_index 	= text_value["index"]
		text_value_values 	= text_value["value"]

		input_value 		= nodes["inputValue"]
		input_value_index 	= input_value["index"]
		input_value_values 	= input_value["value"]

		input_checked 		= nodes["inputChecked"]
		layout 				= document["layout"]
		layout_node_index 	= layout["nodeIndex"]
		bounds 				= layout["bounds"]

		cursor = 0
		html_elements_text = []

		child_nodes = {}
		elements_in_view_port = []
		
		# Refactored to use dict.setdefault() for cleaner logic
		ancestor_exceptions = {
			"a": {"ancestry": {"-1": (False, None)}, "nodes": {}},
			"button": {"ancestry": {"-1": (False, None)}, "nodes": {}},
		}

		def convert_name(node_name, is_clickable):
			if node_name == "a":
				return "link"
			if node_name == "input":
				return "input"
			if node_name == "img":
				return "img"
			if node_name == "button" or is_clickable:
				return "button"
			return "text"

		def find_attributes(attributes, keys):
			values = {}
			for [key_index, value_index] in zip(*(iter(attributes),) * 2):
				if value_index < 0:
					continue
				key = strings[key_index]
				value = strings[value_index]
				if key in keys:
					values[key] = value
					keys.remove(key)
					if not keys:
						return values
			return values

		def add_to_hash_tree(hash_tree, tag, node_id, node_name, parent_id):
			parent_id_str = str(parent_id)
			if parent_id_str not in hash_tree:
				parent_name = strings[node_names[parent_id]].lower()
				grand_parent_id = parent[parent_id]
				add_to_hash_tree(hash_tree, tag, parent_id, parent_name, grand_parent_id)
			is_parent_desc_anchor, anchor_id = hash_tree[parent_id_str]
			value = (True, node_id) if node_name == tag else (True, anchor_id) if is_parent_desc_anchor else (False, None)
			hash_tree[str(node_id)] = value
			return value

		for index, node_name_index in enumerate(node_names):
			node_parent = parent[index]
			node_name = strings[node_name_index].lower()

			# Refactored to use dict to store exceptions
			for tag in ancestor_exceptions:
				is_ancestor_of_tag, tag_id = add_to_hash_tree(ancestor_exceptions[tag]["ancestry"], tag, index, node_name, node_parent)
				ancestor_exceptions[tag]["nodes"][str(index)] = (is_ancestor_of_tag, tag_id)
				
			try:
				cursor = layout_node_index.index(index)
			except:
				continue

			if node_name in black_listed_elements:
				continue

			[x, y, width, height] = bounds[cursor]
			x /= device_pixel_ratio
			y /= device_pixel_ratio
			width /= device_pixel_ratio
			height /= device_pixel_ratio

			elem_left_bound = x
			elem_top_bound = y
			elem_right_bound = x + width
			elem_lower_bound = y + height

			partially_is_in_viewport = (
				elem_left_bound < win_right_bound
				and elem_right_bound >= win_left_bound
				and elem_top_bound < win_lower_bound
				and elem_lower_bound >= win_upper_bound
			)

			if not partially_is_in_viewport:
				continue

			meta_data = []

			# Refactored to use dict to store and access attributes
			element_attributes = find_attributes(
				attributes[index], ["type", "placeholder", "aria-label", "title", "alt"]
			)

			ancestor_exception = {
				tag: ancestor_exceptions[tag]["nodes"].get(str(index), (False, None))
				for tag in ancestor_exceptions
			}
			
			is_ancestor_of_anchor, anchor_id = ancestor_exception.get("a", (False, None))  
			is_ancestor_of_button, button_id = ancestor_exception.get("button", (False, None))
			ancestor_node_key = (
				str(anchor_id) if is_ancestor_of_anchor else str(button_id) if is_ancestor_of_button else None
			)
			ancestor_node = (
				child_nodes.setdefault(str(ancestor_node_key), []) 
				if is_ancestor_of_anchor or is_ancestor_of_button
				else None
			)

			if node_name == "#text" and ancestor_node is not None:
				text = strings[node_value[index]]
				if text in ["•", "|"]:
					continue
				ancestor_node.append({"type": "text", "value": text})
			else:
				if (node_name == "input" and element_attributes.get("type") == "submit") or node_name == "button":
					node_name = "button"
					element_attributes.pop("type", None)
				
				for key, value in element_attributes.items():
					if ancestor_node is not None:
						ancestor_node.append({"type": "attribute", "key": key, "value": value})
					else:  
						meta_data.append(value)

			element_node_value = None
			if node_value[index] >= 0:
				element_node_value = strings[node_value[index]]
				if element_node_value == "|": 
					continue
			elif node_name == "input" and index in input_value_index:
				input_text_index = input_value_index.index(index)
				text_index = input_value_values[input_text_index]
				if text_index >= 0:
					element_node_value = strings[text_index]

			if (is_ancestor_of_anchor or is_ancestor_of_button) and (node_name != "a" and node_name != "button"):
				continue

			elements_in_view_port.append({
				"node_index": str(index),
				"backend_node_id": backend_node_id[index],
				"node_name": node_name,
				"node_value": element_node_value,
				"node_meta": meta_data,
				"is_clickable": index in is_clickable,
				"origin_x": int(x),
				"origin_y": int(y),
				"center_x": int(x + (width / 2)),
				"center_y": int(y + (height / 2)),
			})

		elements_of_interest = []
		id_counter = 0

		for element in elements_in_view_port:
			node_index = element["node_index"]
			node_name = element["node_name"]
			node_value = element["node_value"]
			is_clickable = element["is_clickable"] 
			meta_data = element["node_meta"]

			inner_text = f"{node_value} " if node_value else ""
			meta = ""

			if node_index in child_nodes:
				for child in child_nodes[node_index]:
					entry_type = child["type"]
					entry_value = child["value"]
					if entry_type == "attribute":
						entry_key = child["key"]
						meta_data.append(f'{entry_key}="{entry_value}"')
					else:
						inner_text += f"{entry_value} "
			
			if meta_data:
				meta = f' {" ".join(meta_data)}'
			inner_text = inner_text.strip()
			
			# Refactored to use descriptive variable names
			should_include_element = (
				inner_text != "" or
				node_name in ["link", "input", "img", "button", "textarea"] or
				(node_name == "button" and meta != "")
			)
			if not should_include_element:
				continue
   
			page_element_buffer[id_counter] = element
			
			element_string = f'<{convert_name(node_name, is_clickable)} id={id_counter}{meta}>'
			if inner_text:
				element_string += f'{inner_text}</{convert_name(node_name, is_clickable)}>'
			else:
				element_string += '/>'
			elements_of_interest.append(element_string)
			
			id_counter += 1

		print(f'Parsing time: {time.time() - start:.2f} seconds')
		return elements_of_interest

def start_interaction(model_id, objective, project_name):
	_crawler = Crawler()

	def print_help():
		print(
			"(g) to visit url\n(u) scroll up\n(d) scroll down\n(c) to click\n(t) to type\n" +
			"(h) to view commands again\n(r/enter) to run suggested command\n(o) change objective"
		)

	def get_gpt_command(objective, url, previous_command, browser_content):
		prompt = prompt_template
		prompt = prompt.replace("$objective", objective)
		prompt = prompt.replace("$url", url[:100])
		prompt = prompt.replace("$previous_command", previous_command)
		prompt = prompt.replace("$browser_content", browser_content[:4500])
		response = LLM(model_id=model_id).inference(prompt)
		return response

	def run_cmd(cmd):
		cmd = cmd.split("\n")[0]

		if cmd.startswith("SCROLL UP"):
			_crawler.scroll("up")
		elif cmd.startswith("SCROLL DOWN"):
			_crawler.scroll("down")
		elif cmd.startswith("CLICK"):
			commasplit = cmd.split(",")
			id = commasplit[0].split(" ")[1]
			_crawler.click(id)
		elif cmd.startswith("TYPE"):
			spacesplit = cmd.split(" ")
			id = spacesplit[1]
			text = " ".join(spacesplit[2:])
			text = text[1:-1]
			if cmd.startswith("TYPESUBMIT"):
				text += '\n'  
			_crawler.type(id, text)

		time.sleep(2)

	gpt_cmd = ""
	prev_cmd = ""
	_crawler.go_to_page("google.com")

	try:
		visits = 0

		while True and visits < 5:
			browser_content = "\n".join(_crawler.crawl())
			prev_cmd = gpt_cmd

			current_url = _crawler.page.url
   
			_crawler.screenshot(project_name)
   
			gpt_cmd = get_gpt_command(objective, current_url, prev_cmd, browser_content).strip()
			run_cmd(gpt_cmd)
   
			visits += 1
   
	except KeyboardInterrupt:
		print("\n[!] Ctrl+C detected, exiting gracefully.")
		exit(0)
