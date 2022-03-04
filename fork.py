import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from pathlib import Path

driver = webdriver.Chrome(
	chrome_options = Options().add_experimental_option('prefs',  {
			"download.prompt_for_download": False,
			"download.directory_upgrade": True,
			"plugins.always_open_pdf_externally": True
		}
	)
)
wait = WebDriverWait(driver, 10)
courses = list()
assignments = dict()

driver.get("https://spork.school/assignments")
driver.find_element(By.NAME, "username").send_keys("OV_170704")
driver.find_element(By.NAME, "password").send_keys("explicit14")
driver.find_element(By.XPATH, "//button[text()='LOGIN']").click()
time.sleep(4)
driver.find_element(By.CLASS_NAME, "changeLink").click()
driver.find_element(By.XPATH, "//a[contains(@name, 'close_forever')]").click()
time.sleep(4)

sections = len(driver.find_elements(By.XPATH, "//div[contains(@class, '_3LYW_6tMlVar5D7KrMieOK')]"))

def is_ascii(s):
    return all(ord(c) < 128 for c in s)
def download(url, course, type):
	local_filename = ""

	if type == "asset":  # Fix naming convention to match all course files.
		local_filename = "Courses/" + course + "/Assets/" + url.split('/')[-1]
	elif type == "assignment":
		local_filename = "Courses/" + course + "/Assignments/" + url.split('/')[-1]
	else:
		local_filename = "Courses/" + course + "/" + url.split('/')[-1]

	if Path(local_filename).is_file() == False:
		with requests.get(url, stream = True) as r:
			r.raise_for_status()

			with open(local_filename, 'wb') as f:
				for chunk in r.iter_content(chunk_size=8192):
					f.write(chunk)

	return local_filename

for course in driver.find_elements(By.XPATH, "//table[contains(@class, 'ui very basic table _3UgWrbORLsy9e29ecFnHni')]"):
	assignment_list = list()
	element = None
	not_found = True

	while not_found: # error
		try:
			element = course.find_element(By.XPATH, ".//h4[contains(@class, 'ui header')]")
			not_found = False
		except:
			break

	try:
		list.append(courses, element.text)

		for assignment in course.find_elements(By.XPATH, ".//a[contains(@class, '_1R3G1ZH4LfyQUuWayK3_2x limitedTextWidth')]"):
			if is_ascii(assignment.text):
				list.append(assignment_list, assignment.text)
			elif not is_ascii(assignment.text):
				print("Assignment title not encodable.") #assignment.text.encode('utf-8') #but bytes to str invalid
	except:
		continue

	if len(assignment_list) > 0:
			assignments[element.text] = assignment_list
while True:
	if len(assignments) == len(courses) - 1: #a course doesnt show up
		break
for course in courses:
	try:
		assignments[course]	
	except KeyError:
		continue

	for assignment in assignments[course]:
		try:
			wait.until(EC.presence_of_element_located((By.XPATH, "//a[text() = '" + assignment + "']")))
			
			pdfs = list() #TODO: check for more file-types.
			a = driver.find_element(By.XPATH, "//a[text() = '" + assignment + "']")
			
			a.click()

			wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'lessonSelector')]")))

			for element in driver.find_elements(By.XPATH, "//a[contains(@rel, 'noopener noreferrer')]"):
				list.append(pdfs, element.get_attribute("href"))

			if len(pdfs) > 0:
				for pdf in pdfs:
					download(pdf, course, "assignment")
				
			driver.back()
		except:
			continue
'''
                                                                                                                              
                        ▓▓                                                                                                    
                        ░░▓▓                                                                                                  
                ▓▓░░      ▓▓▓▓                                                                                                
          ░░      ██      ░░██▒▒                                                                                              
          ▓▓      ▒▒▓▓      ▓▓▓▓░░                                                                                            
  ░░      ░░▓▓      ▓▓▓▓    ░░▓▓▓▓░░                                                                                          
  ▓▓▓▓      ▒▒▓▓      ▓▓▓▓    ░░▓▓▓▓                                                                                          
  ░░▓▓▒▒      ██▒▒    ░░██░░    ▓▓▓▓▓▓                                                                                        
    ▓▓██      ░░██░░    ▒▒██    ░░▓▓▓▓▒▒                                                                                      
    ░░▓▓▓▓      ▒▒██      ██▓▓    ▓▓▓▓▓▓▒▒                                                                                    
      ▓▓▓▓▓▓      ████    ░░██▒▒    ▓▓▓▓▓▓░░                                                                                  
        ▓▓▓▓▒▒    ░░██▓▓    ▓▓██░░  ▓▓▓▓▓▓██                                                                                  
        ██▓▓▓▓░░    ▓▓▓▓░░  ░░▓▓▓▓  ░░▓▓██████                                                                                
        ▒▒▓▓▓▓▓▓      ██▓▓    ▒▒▓▓▓▓  ▓▓▓▓████▒▒                                                                              
          ▓▓▓▓██▓▓    ▒▒▓▓▓▓    ▓▓▓▓░░  ████▓▓░░                                                                              
          ░░▓▓▓▓██▓▓    ▓▓▓▓▓▓  ░░▓▓██  ▒▒▒▒░░                                                                                
            ▓▓██▓▓▓▓▒▒  ░░▓▓▓▓░░  ▓▓██▒▒  ░░░░    ░░                                                                          
            ░░▓▓▓▓▓▓▓▓░░  ▓▓▓▓██  ░░▓▓░░          ░░                                                                          
              ▓▓▓▓▓▓▓▓▓▓  ░░▓▓██▒▒  ▒▒░░                                                                                      
              ░░▓▓▓▓▓▓▓▓██  ▓▓▓▓▒▒  ▒▒                                                                                        
                ▒▒▓▓▓▓██▓▓░░░░▒▒░░                                                                                            
                  ▓▓▓▓██▓▓▒▒▒▒░░   ( ͡° ͜ʖ ͡°)                                                                                           
                  ▒▒▓▓▓▓▓▓▒▒░░                      ▒▒                                                                        
                    ▒▒▒▒▒▒░░░░                    ▒▒░░                                                                        
                      ▒▒░░░░                  ░░▒▒░░░░                                                                        
                      ░░░░░░              ░░▒▒▒▒░░░░░░                                                                        
                        ░░░░            ▒▒▒▒░░░░░░░░░░                                                                        
                            ░░      ░░▒▒░░░░░░░░░░░░░░                                                                        
                              ░░░░  ▒▒░░░░░░░░░░░░░░░░                                                                        
                                  ░░▒▒▒▒░░▒▒▒▒▓▓▒▒░░░░░░                                                                      
                                                ░░▒▒▒▒░░░░                                                                    
                                                  ░░▒▒░░░░▒▒                                                                  
                                                    ▒▒▒▒░░▒▒░░                                                                
                                                      ░░░░░░░░░░                                                              
                                                        ▒▒  ░░▒▒░░                                                            
                                                          ▒▒▒▒░░▒▒░░                                                          
                                                            ▓▓▒▒░░▒▒░░                                                        
                                                              ▒▒▓▓  ▒▒░░                                                      
                                                                ░░▓▓  ▒▒░░                                                    
                                                                ░░░░▓▓  ▒▒░░                                                  
                                                                  ▒▒░░▒▒  ▒▒░░                                                
                                                                    ▒▒▒▒░░  ▒▒░░                                              
                                                                      ░░▓▓  ░░▒▒                                              
                                                                      ░░░░▓▓  ░░▒▒░░                                          
                                                                        ▒▒░░▓▓  ░░▒▒░░                                        
                                                                          ░░▒▒░░  ░░▒▒░░                                      
                                                                            ░░▓▓    ░░▒▒░░                                    
                                                                            ░░░░▓▓    ░░▒▒░░                                  
                                                                              ▒▒░░▓▓    ░░▒▒░░                                
                                                                                ▒▒▒▒▒▒    ░░▒▒▓▓                              
                                                                                  ░░▒▒      ░░░░▓▓                            
                                                                                    ▒▒░░░░  ░░▒▒▒▒░░                          
                                                                                    ░░░░░░░░  ░░▒▒░░                          
                                                                                      ░░░░░░░░  ░░▒▒▒▒                        
                                                                                        ▒▒▒▒░░░░    ▒▒                        
                                                                                          ░░░░▒▒░░  ░░▒▒░░░░                  
                                                                                            ░░░░░░░░  ░░▒▒▒▒░░                
                                                                                              ▒▒▒▒░░    ░░▒▒░░▒▒              
                                                                                                ▒▒░░        ░░▒▒░░░░          
                                                                                                  ░░░░        ░░▒▒▒▒░░░░      
                                                                                                  ▒▒░░          ░░▒▒▒▒░░░░    
                                                                                                  ░░░░░░          ░░▒▒▒▒░░░░  
                                                                                                    ░░░░░░          ░░▓▓▒▒▒▒░░
                                                                                                    ▒▒░░▒▒            ▒▒▒▒▒▒▒▒
                                                                                                    ▒▒░░▒▒▓▓          ░░▓▓░░▒▒
                                                                                                      ▒▒░░▓▓▒▒          ▓▓▒▒▒▒
                                                                                                      ░░░░░░▒▒░░░░    ░░▒▒▒▒▓▓
                                                                                                        ░░▒▒░░░░░░▓▓▓▓░░░░░░▓▓
                                                                                                          ░░▒▒▒▒▒▒░░▒▒░░░░▒▒░░
                                                                                                              ░░▒▒▒▒▓▓▒▒▓▓▒▒  
'''