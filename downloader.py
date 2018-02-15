import requests
from bs4 import BeautifulSoup
import sqlite3
import time

def get_page(roll):
	params = {'g-recaptcha-response' : '' ,'roll': str(roll) , 'type' : 'R'}

	r = ''
	while r == '':
		try :
			r = requests.post("http://result.ietlucknow.ac.in/ODD201718", data = params)
		except :
			print("Connection refused by the server..")
			print("Retrying in 2 seconds")
			time.sleep(2)
			print("Retrying now....")
			continue

	soup = BeautifulSoup(r.text, 'html5lib')
	return soup

def get_name(soup):
	try :
		name = soup.find_all('td')[1].get_text()
		return name
	except IndexError :
		return None

def get_SGPA(soup):
	try :
		SGPA = soup.find_all('td')[93].get_text()
		SGPA = float(SGPA)
		return SGPA
	except IndexError:
		return None

def get_branch(soup) :
	try :
		branch = soup.find_all('td')[9].get_text()
		branch = branch.split()[1:-3]     
		branch = ' '.join(branch)  #collected branchname
		return branch
	except IndexError :
		return None

def result_downloader(first_roll,last_roll):
	for i in range(first_roll,last_roll+1) :
		new_page = get_page(i)
		new_name = get_name(new_page)
		new_SGPA = get_SGPA(new_page)
		new_branch = get_branch(new_page)
		new_roll_number = i

		if new_name is None and new_SGPA is None:
			continue
		else :
			cur.execute('SELECT Names FROM Results WHERE  Names = ? ', (new_name, ) )
			row = cur.fetchone()
			cur.execute(''' INSERT INTO Results (Rollnumber,Names,SGPA,Branch) VALUES (?,?,?,?) ''', (new_roll_number,new_name,new_SGPA,new_branch))
			print('Downloading data of roll number', i)
			conn.commit()

print("Enter the name of the file on which you want to save this data ... ")
database = input()
database = database+'.sqlite'  #name of the database

conn = sqlite3.connect(database)
cur = conn.cursor()
cur.execute(''' DROP TABLE IF EXISTS Results ''' )
cur.execute(''' CREATE TABLE Results (Rollnumber INTEGER ,Names TEXT, SGPA INTEGER , Branch TEXT)  ''')

print("Enter the year code... (ie. First two digits of your roll number) ")
year_code = int(input())
print("Enter the branch_Code... (ie. 31 for EC, 32 for EI , 10 for CS , 13 for IT  etc) ")
branch_Code = int(input())

first_roll = year_code*100000000 + 5200000 + branch_Code*1000 + 1
last_roll = first_roll + 70 #at max

test = get_page(first_roll)
test = get_branch(test)


lateral_first_roll = (year_code + 1)*100000000 + 5200000 + branch_Code*1000 + 9*100 + 1
lateral_last_roll = lateral_first_roll + 14

print("Downloading the result.")

result_downloader(first_roll,last_roll)
print("Downloading Lateral Entry's result.")
result_downloader(lateral_first_roll,lateral_last_roll)
print("Downloaded the result. Stored at", database)

