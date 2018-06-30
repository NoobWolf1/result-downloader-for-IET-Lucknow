import requests
from bs4 import BeautifulSoup
import sqlite3
import time

def get_page(roll):
	params = {'g-recaptcha-response' : '' , 'result': 'btech' , 'roll': str(roll)}
	r = ''
	while r =='':
		try:
			r = requests.post('http://result.ietlucknow.ac.in/201617', data = params)
		except:
			print("Connection refused by the server..")
			print("Retrying in 2 seconds")
			time.sleep(2)
			print("Retrying now....")
			continue
	soup = BeautifulSoup(r.text, 'html5lib')
	return soup


def get_data(soup):
	try:
		name = soup.find_all('td')[1].get_text()

		branch = soup.find_all('td')[9].get_text()

		marks = soup.find_all('td')[111].get_text()
		marks = float(marks)
		
		SGPA_Sem1 = soup.find_all('td')[112].get_text()
		SGPA_Sem1 = float(SGPA_Sem1)

		SGPA_Sem2 = soup.find_all('td')[113].get_text()
		SGPA_Sem2 = float(SGPA_Sem2)

		CGPA = soup.find_all('td')[114].get_text()
		CGPA = float(CGPA)

		carry_papers = soup.find_all('td')[107].get_text()
		carry_papers = carry_papers.strip()

		if carry_papers == ',':
			carry_papers = carry_papers[1:]
			carry_papers = '0'
		elif carry_papers[-1] == ',':
			carry_papers = carry_papers[:-1]

			carry_papers = str(len(carry_papers.split(','))) + ' (' + carry_papers+')'

		elif carry_papers[0]==',':
			carry_papers = carry_papers[1:]
			carry_papers = str(len(carry_papers.split(','))) + ' (' + carry_papers+')'

		else:

			carry_papers = str(len(carry_papers.split(','))) + ' (' + carry_papers+')'


	
		return name,branch,marks,SGPA_Sem1,SGPA_Sem2,CGPA,carry_papers
	except IndexError:
		return None, None, None, None, None, None, None


def result_downloader(first_roll,last_roll):
	for roll in range(first_roll, last_roll+1):
		new_page = get_page(roll)
		new_name, new_branch, new_marks, new_SGPA_Sem1, new_SGPA_Sem2, new_CGPA, new_carry_papers = get_data(new_page)
		new_roll_number = roll

		if new_name is None:
			continue
		else :

			cur.execute('SELECT Names FROM Final_Results WHERE  Names = ? ', (new_name, ) )
			row = cur.fetchone()
			cur.execute(''' INSERT INTO Final_Results (Rollnumber,Names,Branch,Marks,SGPA1,SGPA2,CGPA,CarryPapers) VALUES (?,?,?,?,?,?,?,?) ''', (new_roll_number,new_name,new_branch,new_marks,new_SGPA_Sem1,new_SGPA_Sem2,new_CGPA,new_carry_papers))
			print('Downloading data of roll number', roll)

		conn.commit()

print("Enter the name of the file on which you want to save this data ... ")
database = input()
database = database+'.sqlite' 

conn = sqlite3.connect(database)
cur = conn.cursor()
cur.execute(''' DROP TABLE IF EXISTS Results ''' )
cur.execute(''' CREATE TABLE Final_Results
 (Rollnumber INTEGER ,Names TEXT, Branch TEXT,Marks INTEGER,SGPA1 INTEGER , SGPA2 INTEGER , CGPA INTEGER , CarryPapers TEXT)  ''')

print("Enter the year code... (ie. First two digits of your roll number) ")
year_code = int(input())
print("Enter the branch_Code... (ie. 31 for EC, 32 for EI , 10 for CS , 13 for IT  etc) ")
branch_Code = int(input())

first_roll = year_code*100000000 + 5200000 + branch_Code*1000 + 1
last_roll = first_roll + 70 #at max


lateral_first_roll = (year_code + 1)*100000000 + 5200000 + branch_Code*1000 + 9*100 + 1
lateral_last_roll = lateral_first_roll + 14

print("Downloading the result.")
result_downloader(first_roll,last_roll)
print("Downloading Lateral Entry's result.")
result_downloader(lateral_first_roll,lateral_last_roll)
print("Downloaded the result. Stored at", database)




