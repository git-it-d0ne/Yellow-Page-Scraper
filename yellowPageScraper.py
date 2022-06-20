import requests, random, time, socket
import pandas as pd
from bs4 import BeautifulSoup

urls = []
response_waits = [5, 6, 7, 8, 9, 10]
response_wait = random.choice(response_waits)

# Create an array of user agents to loop through while testing domain links to keep from getting disconnected
user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/100.0.1185.39',
'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Vivaldi/4.3',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Vivaldi/4.3']

referers = ["https://google.com", "https://www.yahoo.com/", "https://duckduckgo.com/", "https://www.msn.com/", "https://www.ask.com/"]

base_url = "https://www.yellowpages.com"
url_file = "urls.txt"
with open(url_file) as infile:
	for line in infile:
		if line not in urls:
			urls.append(line.replace("\n", ""))
	infile.close()

def get_potential_business_data():
	with open("Potential Businesses.txt", 'w') as outfile:
		global urls
		for url in urls:
				try:
					session = requests.Session()
					headers={'User-Agent': random.choice(user_agents), "Referer": random.choice(referers)}
					response = session.get(url, headers=headers, timeout=15)
					page = BeautifulSoup(response.text, 'html.parser')
					
					results = page.findAll('div', {'class': 'info-section'})
					for result in results:
						info_sections = result.findAll('div', {'class': 'links'})
						for section in info_sections:
							for entry in info_sections:
								if len(entry) < 1:
									business_url = result.find('a', {'class': 'business-name'})
									print(business_url['href'])
									new_response = base_url + business_url['href']
									
									new_session = session.get(new_response, headers=headers, timeout=15)
									page = BeautifulSoup(new_session.text, 'html.parser')
									print(new_session)

									business = page.find('h1', {'class': 'business-name'}).text
									outfile.write(business + ";")
									print(business)
									try:
										email_element = page.find('a', {'class': 'email-business'})
										email = email_element['href']
										outfile.write(email.replace("mailto:", "") + ";")
										print(email)
									except TypeError:
										outfile.write("Email Missing;")
										print("Email Missing")
									try:
										phone_number = page.find('p', {'class': 'phone'}).text
										outfile.write(phone_number.replace("Phone:  ", "") + ";")  
										print(phone_number)
									except AttributeError:
										outfile.write("Phone Number Missing;")
										print("Phone Number Missing,")
									try:
										address = page.find('span', {'class': 'address'}).span.text
										outfile.write(address + "\n")
										print(address)
									except AttributeError:
										outfile.write("Address Missing\n")
										print("Address missing")
									
								else:
									print("Website already exists")
					
				except socket.timeout:
					continue
				print("Taking a short break...\n")
				time.sleep(response_wait)
		outfile.close()

	with open("Potential Businesses.txt") as infile, open("Revised Businesses.txt", 'w') as outfile:
		for line in infile:
			if "Email Missing" not in line:
				outfile.write(line)
		outfile.close()
		infile.close()



def write_to_excel():
	business_file = "Revised Businesses.txt"
	excel_file = "New " + business_file.replace('.txt', '.xlsx') 
	data = pd.read_csv(business_file, sep=";", header=None)
	data.columns = ['Business Name', 'Email', 'Phone Number', 'Address']
	data.to_excel(excel_file, index=False)


def run_program():
	user_choice = input("What do you want to do?\n1. Find potential businesses\n"
		"2. Write businesses to spreadsheet\nType 1 or 2 and press enter...\n")

	if user_choice == '1':
		get_potential_business_data()
	if user_choice == '2':
		write_to_excel()

run_program()