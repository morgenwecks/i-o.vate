import urllib.request
import io
import datetime
import os
import pdftotext
import pickle
import re
import numpy as np
import pandas as pd


#get the HK journals, week-wise


def grab_hk_journals():
    
	today = datetime.date.today()
	date_list = [today - datetime.timedelta(days=x) for x in range(0, 10000)]

	for index,date in enumerate(date_list):
		keydate = date.strftime("%d%m%Y")
		
		print("now at", keydate)
		link = ('http://ipsearch.ipd.gov.hk/hkipjournal/%s/Patent_%s.pdf' % (keydate, keydate))
		print(link)
		try:
			temp_pdf = urllib.request.urlretrieve(link, '%s.pdf' % keydate)
			
			with open("%s.pdf" % keydate, "rb") as f:
				pdf = pdftotext.PDF(f)
			
			

			text = "\n\n".join(pdf)
			text_file = open("%s.txt" %keydate, "w")
			text_file.write(text)
			text_file.close()
			
			
			print('i am opening the name file now')
			with open("%s.txt" %keydate, 'r') as f:
				text = f.read()
			print(len(text))
			
			def getnonChinese(context):
				print('getnonchinese started')
				filtrate = re.compile(u'[\u4e00-\u9fff]') # Chinese unicode range
				context = filtrate.sub(r'', context) # remove all Chinese characters
				print('i am returning the context now')
				return context
			
			text = getnonChinese(text)
			print(len(text))
				
# # Function to get rid of the Chinese characters

			# Get rid off the first page of the pdf file
			text = text[text.find('Requests to Record Published (Arranged by International\nPatent Classification)'):]
			print(len(text))
			# Divide the PDF file per types of Patents
			# Part 1 : Requests to Record Designated Patent Applications published under section 20 of the Patents Ordinance
			# Part 2 : Granted Standard Patents published under section 27 of the Patents Ordinance
			# Part 3 : Granted Short-term Patents published under section 118 of the Patents Ordinance
			part1 = text[:text.find("Requests to Record Published (Arranged by Publication No.)")]
			part2 = text[text.find("Standard Patents Granted (Arranged by International Patent\nClassification)"):text.find("Standard Patents Granted (Arranged by Publication No.)")]
			part3 = text[text.find("Short-term Patents Granted (Arranged by International Patent\nClassification)"):text.find("Short-term Patents Granted (Arranged by Publication No.)")]
			print(part3)
# Create empty dictionnary with keys representing the INID Codes
			def generate_allindex():
				d = {}
				d['51'] = ''
				d['11'] = ''
				d['11A'] = ''
				d['13'] = ''
				d['25'] = ''
				d['21'] = ''
				d['22'] = ''
				d['86'] = ''
				d['86A'] = ''
				d['87'] = ''
				d['30'] = ''
				d['62'] = ''
				d['54'] = ''
				d['73N'] = ''
				d['73C'] = ''
				d['71N'] = ''
				d['71C'] = ''
				d['72'] = ''
				d['74N'] = ''
				d['74C'] = ''
				return d

# Create Functions to Parse the data/information of each labels/features for all Patents

			def parser51(entry):
				if not entry:
					return np.nan
				else:
					fiftyone = "".join(entry.split('\n'))
					fiftyone = "".join(re.findall(r'\b[A-Z0-9]{4}\b|$', entry))
					return fiftyone

			def parser11(entry):
				if not entry:
					return np.nan
				return re.findall(r'[\d]{7}[*]?|$', entry)[0]

			def parser11A(entry):
				if not entry:
					return np.nan
				return re.findall("[A-Z]{2}[\d]+.+[\d]*[A-Z]|$", entry)[0]

			def parser13(entry):
				if not entry:
					return np.nan
				return re.findall(r'\b[A-Z]{1}\b|$' ,entry)[0]


			def parser25(entry):
				if not entry:
					return np.nan
				return "".join(entry.split('\n')[0].strip())

			def parser21(entry):
				if not entry:
					return np.nan
				return "".join(entry.strip())

			def parser22(entry):
				if not entry:
					return np.nan
				return "".join(entry.split("\n")[0]).strip()

			def parser86(entry):
				if not entry:
					return np.nan
				return "".join(entry.split('\n')[0].strip())

			def parser86A(entry):
				if not entry:
					return np.nan
				return "".join(re.findall(r'[A-Z]+.[A-Z]{2}\d+.\d+', entry))

			def parser87(entry):
				if not entry:
					return np.nan
				return "".join(entry.split('\n')[0].strip())

			def parser30(entry):
				if not entry:
					return np.nan
				return ",".join(re.findall(r'\d{2}.\d{2}.\d{4}\s+\w{2}.+\d+.[A-Z0-9,]+', entry))

			def parser62(entry):
				if not entry:
					return np.nan
				return ",".join(re.findall(r'\d{2}.\d{2}.\d{4}\s+\w{2}.\d+.[A-Z0-9]+',entry))

			def parser54(entry):
				if not entry:
					return np.nan
				return ''.join(re.findall(r'[A-Z]+[^A-Za-z]', entry)).strip()

			def parser73N(entry):
				if not entry:
					return np.nan
				else:
					CompanyName = entry.split('\n')[0]
					return CompanyName

			def parser73C(entry):
				if not entry:
					return np.nan
				else:
					Country = re.sub(r'[^a-zA-Z\s]','', entry)
					Country = "".join(Country.strip().split('\n')[-2:])
					return Country

			def parser71N(entry):
				if not entry:
					return np.nan
				else:
					CompanyName = entry.split('\n')[0]
					return CompanyName

			def parser71C(entry):
				if not entry:
					return np.nan
				else:
					Country = re.sub(r'[^a-zA-Z\s]','', entry)
					Country = "".join(Country.strip().split("\n")[-2:])
					return Country

			def parser72(entry):
				if not entry:
					return np.nan
				else:
					Name = re.sub(r'[^a-zA-Z\s,]','', entry)
					Name = "".join(Name.split('\n')).strip()
					return Name

			def parser74N(entry):
				if not entry:
					return np.nan
				else:
					CompanyName = entry.split('\n')[0].strip()
					return CompanyName

			def parser74C(entry):
				if not entry:
					return np.nan
				else:
					Country = re.sub(r'[^a-zA-Z\s]','', entry)
					Country = Country.strip().split('\n')[-1].strip()
					return Country

# Write a Function to create a list of patents and their key-value pairs
			def get_list_patent(part):
				dlist =[]
				for patent in part:
				
					d = generate_allindex()
					for entry in patent:
						if entry.startswith('[51]'):
							d['51'] = parser51(entry)
						elif entry.startswith('[11]'): 
							d['51'] += parser51(entry)
							d['11'] = parser11(entry)
							d['11A'] = parser11A(entry)
						elif entry.startswith('[13]'):
							d['13'] = parser13(entry[5:])
						elif entry.startswith('[25]'):
							d['25'] = parser25(entry[5:])
						elif entry.startswith('[21]'):
							d['21'] = parser21(entry[5:])
						elif entry.startswith('[22]'):
							d['22'] = parser22(entry[5:])
						elif entry.startswith('[86]'):
							d['86'] = parser86(entry[5:])
							d['86A'] = parser86A(entry)
						elif entry.startswith('[87]'):
							d['87'] = parser86(entry[5:])
						elif entry.startswith('[30]'):
							d['30'] = parser30(entry[5:])
						elif entry.startswith('[62]'):
							d['62'] = parser62(entry)
						elif entry.startswith('[54]'):
							d['54'] = parser54(entry)
						elif entry.startswith('[73]'):
							d['73N'] = parser73N(entry[5:])
							d['73C'] = parser73C(entry)
						elif entry.startswith('[71]'):
							d['71N'] = parser71N(entry[5:])
							d['71C'] = parser71C(entry)
						elif entry.startswith('[72]'):
							d['72'] = parser72(entry[5:])
						elif entry.startswith('[74]'):
							d['74N'] = parser74N(entry[5:])
							d['74C'] = parser74C(entry)
					dlist.append(d)
				print(dlist)
				return dlist

# Write a function to create the Dataframe per types of patent
			def dataframes(part):
				df = pd.DataFrame(get_list_patent(part))
				df = df[['51','11','11A','13','25','21','22','86','86A','87','30','62','54','73N','73C','71N','71C','72','74N','74C']]
				df = df[:-1]
				return df

# PART 1:  "Requests to Record Designated Patent Applications published under section 20 of the Patents Ordinance"
# get rid of the Header on each pages
			part1 = part1.replace("Journal No.:",'')
			part1 = part1.replace('\x0c','')
			part1 = part1.replace("Section Name:","")
			part1 = part1.replace('Publication Date:','')
			part1 = part1.replace('Requests to Record Published (Arranged by International\nPatent Classification)','')
			part1 = part1.replace('Arranged by International Patent Classification', '')

			line = "_______________________________________________________________________"
			part1 = part1.split(line)

			patent_part1 = []
			for patent in part1:
				patent_part1.append(re.findall(r'\[\d+\][^\[]*', patent, re.S))

			df1 = dataframes(patent_part1)

# PART 2:  "Granted Standard Patents published under section 27 of the Patents Ordinance"
# get rid of the Header on each pages
			part2 = part2.replace("Journal No.:",'')
			part2 = part2.replace('\x0c','')
			part2 = part2.replace("Section Name: ()","")
			part2 = part2.replace('Publication Date:','')
			part2 = part2.replace('Standard Patents Granted (Arranged by International Patent\nClassification)','')
			part2 = part2.replace('Arranged by International Patent Classification', '')
			part2 = part2.replace('Section Name: ()  Standard Patents Granted ()', '')

			part2 = part2.split(line)
			patent_part2 = []
			for patent in part2:
				patent_part2.append(re.findall(r'\[\d+\][^\[]*', patent, re.S))

			df2 = dataframes(patent_part2)

# PART 3:  "Granted Short-term Patents published under section 118 of the Patents Ordinance"
# get rid of the Header on each pages
# get rid of the Header on each pages
			part3 = part3.replace("Journal No.: 803",'')
			part3 = part3.replace('\x0c','')
			part3 = part3.replace("Section Name: ()","")
			part3 = part3.replace('Publication Date: 17-08-2018','')
			part3 = part3.replace('Short-term Patents Granted (Arranged by International Patent\nClassification)','')
			part3 = part3.replace('Arranged by International Patent Classification', '')
			part3 = part3.replace('Section Name: ()  Short-term Patents Granted ()', '')

			part3 = part3.split(line)
			patent_part3 = []
			for patent in part3:
				patent_part3.append(re.findall(r'\[\d+\][^\[]*', patent, re.S))

			df3 = dataframes(patent_part3)

# CREATE FINAL DATAFRAME :
			def final_Dataframe():
				final1 = pd.concat([df1,df2,df3],keys=['Type1','Type2','Type3'])
				final = final1.reset_index()
				final.drop(['level_1'], inplace = True, axis=1)
				final = final.replace(r'^\s*$', np.nan, regex=True)
				final.rename(columns={'level_0': 'Patent Type'}, inplace=True)
				return final
			
			df_final = final_Dataframe()
			print(df_final)
			save_frame = open('%s.pickle' % keydate,'wb')
			pickle.dump(df_final,save_frame)
			save_frame.close()
			print("file saved")

		except Exception as e:
			print(e)
			continue
grab_hk_journals()

