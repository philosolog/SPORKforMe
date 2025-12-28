import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()

options = Options()
options.add_experimental_option(
	"prefs",
	{
		"download.prompt_for_download": False,
		"download.directory_upgrade": True,
		"plugins.always_open_pdf_externally": True,
	},
)
service = Service(executable_path="./chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)
courses: list[str] = list()
assignments: dict[str, list[str]] = dict()

driver.get("https://spork.school/assignments")
username = os.getenv("SPORK_USERNAME")
password = os.getenv("SPORK_PASSWORD")
if not username or not password:
	raise ValueError("SPORK_USERNAME or SPORK_PASSWORD not set in environment variables.")

driver.find_element(By.NAME, "username").send_keys(username)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.XPATH, "//button[text()='LOGIN']").click()
time.sleep(4)
driver.find_element(By.CLASS_NAME, "changeLink").click()
driver.find_element(By.XPATH, "//a[contains(@name, 'close_forever')]").click()
time.sleep(4)

sections = len(
	driver.find_elements(By.XPATH, "//div[contains(@class, '_3LYW_6tMlVar5D7KrMieOK')]")
)

def is_ascii(s: str) -> bool:
	return all(ord(c) < 128 for c in s)
def download(url: str, course: str, type: str) -> str:
	local_filename = ""

	if type == "asset":  # TODO: Fix naming convention to match all course files.
		local_filename = "Courses/" + course + "/Assets/" + url.split("/")[-1]
	elif type == "assignment":
		local_filename = "Courses/" + course + "/Assignments/" + url.split("/")[-1]
	else:
		local_filename = "Courses/" + course + "/" + url.split("/")[-1]

	if not Path(local_filename).is_file():
		with requests.get(url, stream=True) as r:
			r.raise_for_status()

			with open(local_filename, "wb") as f:
				for chunk in r.iter_content(chunk_size=8192):
					f.write(chunk)

	return local_filename

for course_elem in driver.find_elements(
	By.XPATH, "//table[contains(@class, 'ui very basic table _3UgWrbORLsy9e29ecFnHni')]"
):
	assignment_list: list[str] = list()
	element = None
	not_found = True

	while not_found: # *: Catch error
		try:
			element = course_elem.find_element(
				By.XPATH, ".//h4[contains(@class, 'ui header')]"
			)
			not_found = False
		except Exception:
			break

	try:
		if element is not None:
			courses.append(element.text)

			for assignment_elem in course_elem.find_elements(
				By.XPATH,
				".//a[contains(@class, '_1R3G1ZH4LfyQUuWayK3_2x limitedTextWidth')]",
			):
				if is_ascii(assignment_elem.text):
					assignment_list.append(assignment_elem.text)
				elif not is_ascii(assignment_elem.text):
					print("Assignment title not encodable.") # *: assignment.text.encode("utf-8"), but bytes to str is invalid
	except Exception:
		continue

	if len(assignment_list) > 0:
		if element is not None:
			assignments[element.text] = assignment_list
while True:
	if len(assignments) == len(courses) - 1: # *: When a course doesnt show up
		break
for course in courses:  # TODO: Assets
	try:
		assignments[course]
	except KeyError:
		continue

	for assignment in assignments[course]:
		try:
			wait.until(
				EC.presence_of_element_located(
					(By.XPATH, "//a[text() = '" + assignment + "']")
				)
			)

			pdfs: list[str] = list()  # TODO: check for more file-types.
			a = driver.find_element(By.XPATH, "//a[text() = '" + assignment + "']")

			a.click()

			wait.until(
				EC.presence_of_element_located(
					(By.XPATH, "//div[contains(@class, 'lessonSelector')]")
				)
			)

			for element in driver.find_elements(
				By.XPATH, "//a[contains(@rel, 'noopener noreferrer')]"
			):
				href = element.get_attribute("href")
				if href:
					pdfs.append(href)

			if len(pdfs) > 0:
				for pdf in pdfs:
					download(pdf, course, "assignment")

			driver.back()
		except Exception:
			continue

print("Download sequence completed.")
