import scrapy
from arg_calendar.items import ArgCalendarItem
from arg_calendar.items import CaseItem
from urlparse import urljoin

class ArgCalendarSpider(scrapy.Spider):
	name = 'ArgCalendar'
	allowed_domains = ["www.supremecourt.gov"]
	start_urls = ["http://www.supremecourt.gov/oral_arguments/argument_calendars.aspx"]

	'''
	Extracts all urls of monthly calendars for spider to crawl through
	'''
	def parse(self, response):
		for href in response.xpath('//ul/li/a[2]/@href'):
			url = urljoin('http://www.supremecourt.gov/oral_arguments/', href.extract())
			yield scrapy.Request(url, callback=self.parse_calendar)

	'''
	Extracts data from the monthly calendar, recording the url and term 
	of the calendar and recording the name, date, docket number, 
	consolidated cases, and url of each case in the monthly calendar
	'''
	def parse_calendar(self, response):
		calendar = ArgCalendarItem()
		calendar['link'] = response.url
		term = response.xpath('//table/tr[1]/td/p[4]/b/span/text()')[0].extract()
		calendar['term'] = str(' '.join(term.split()))
		oct_thru_jan = ['http://www.supremecourt.gov/oral_arguments/calendars/MonthlyArgumentCalOctober2015.html',
		'http://www.supremecourt.gov/oral_arguments/calendars/MonthlyArgumentCalNovember2015.html',
		'http://www.supremecourt.gov/oral_arguments/calendars/MonthlyArgumentCalDecember2015.html',
		'http://www.supremecourt.gov/oral_arguments/calendars/MonthlyArgumentCalJanuary2016.html']
		feb_thru_march = ['http://www.supremecourt.gov/oral_arguments/calendars/MonthlyArgumentCalFebruary2016.html',
		'http://www.supremecourt.gov/oral_arguments/calendars/MonthlyArgumentCalMarch2016.html']
		april = ['http://www.supremecourt.gov/oral_arguments/calendars/MonthlyArgumentCalApril2016.html']

		if response.url in oct_thru_jan:
			calendar['cases'] = self.oct_thru_jan_parse_cases(response)
		elif response.url in feb_thru_march:
			calendar['cases'] = self.feb_thru_march_parse_cases(response)
		else:
			calendar['cases'] = self.april_parse_cases(response)
		yield calendar

	'''
	Helper function for parse_calendar
	Returns a list of cases in the monthly calendar recording the name,
	date, docket number, consolidated cases, and url of each case. 
	'''
	def april_parse_cases(self, response):
		
		box_xpath = '//*[@id="ctl00_ctl00_MainEditable_mainContent_RadEditor1"]/div/table[2]/tr/td'

		name = ''
		date = ''
		case = CaseItem()

		temp_cases = [] #for consolidated
		cases = []

		for box in response.xpath(box_xpath):
			for line in box.xpath('p'):

				if line.xpath('b'): #bold tag indicates a date
					if line.xpath('b/span/text()').extract()[0].strip() != '':
						date = line.xpath('b/span/text()').extract()[0].strip()

				elif line.xpath('span/a/@href'): #line holds a link to a docket

					if name != '': #we have reached a new case, and need to append the current case
						if ')' in name: #case is consolidated w others
							case['name'] = str(' '.join(name[1:].split())) #remove parens + white space
							temp_cases.append(case)
						else: #case stands alone
							case['name'] = str(' '.join(name.split())) #remove white space
							case['consolidated_with'] = None
							cases.append(case)
						#initialize a new case
						case = CaseItem()
						name = ''
					#start collecting new case info
					link = line.xpath('.//span/a/@href').extract()[0]
					case['link'] = urljoin(response.url, link)
					case['docket'] = line.xpath('.//span/a/text()').extract()[0]
					case['date'] = str(date)
					name = line.xpath('span/text()')[1].extract().strip()

				elif line.xpath('span/text()'): # line contains text but no link
					text = line.xpath('span/text()').extract()[0].strip() #get text, remove white space

					if text == '' and name: #text is empty, case is complete

						if ')' in name: #case is consolidated w others
							case['name'] = str(' '.join(name[1:].split()))
							temp_cases.append(case)

						else: #case stands alone
							case['name'] = str(' '.join(name.split()))
							case['consolidated_with'] = None
							cases.append(case)

						#list of consolidated cases is complete
						#Set case to be consolidated w every other case in temp_cases
						if temp_cases != []:
							for index in range(len(temp_cases)):
								consolidated = []
								for item in temp_cases[index+1:]+temp_cases[:index]:
									consolidated.append(item['name'])
								temp_cases[index]['consolidated_with'] = consolidated

							cases = cases + temp_cases
							temp_cases = []

						case = CaseItem()
						name = ''

					elif '(' not in text and name: #Text is part of a name
						name = name + ' ' + text
		return cases

	def feb_thru_march_parse_cases(self, response):
		#for march 
		#for feb 
		box_xpath = '//*[@id="ctl00_ctl00_MainEditable_mainContent_RadEditor1"]/div/table/tr[2]/td/table/tr/td/table/tr/td'
		name = ''
		date = ''
		temp_cases = []
		cases = []

		for box in response.xpath(box_xpath):
			for line in box.xpath('.//p'):

				if line.xpath('b'):
					if line.xpath('b/span/text()').extract()[0].strip() != '':
						date = line.xpath('b/span/text()').extract()[0].strip()

				elif line.xpath('a/@href'):
					if name: #we have reached a new case and need to append current case
						if ')' in name:
							case['name'] = str(' '.join(name[1:].split()))
							temp_cases.append(case)
						else:
							case['name'] = str(' '.join(name.split()))
							case['consolidated_with'] = None
							cases.append(case)

					case = CaseItem()
					link = str(line.xpath('a/@href')[0].extract())
					case['link'] = urljoin(response.url, link)
					case['date'] = str(date)
					case['docket'] = str(line.xpath('a/span/text()').extract()[0])

					name = line.xpath('span/text()').extract()[1].strip()

				elif line.xpath('span/text()'):
					text = line.xpath('span/text()').extract()[0].strip()

					if '(' not in text and name: #Text is part of a name
						name = name + ' ' + text
					else:
						if name: #we have reached a new case and need to append current case
							if ')' in name:
								case['name'] = str(' '.join(name[1:].split()))
								temp_cases.append(case)
							else:
								case['name'] = str(' '.join(name.split()))
								case['consolidated_with'] = None
								cases.append(case)
							case = CaseItem()
							name = ''

						#list of consolidated cases is complete
						#Set case to be consolidated w every other case in temp_cases
						if temp_cases != []:
							for index in range(len(temp_cases)):
								consolidated = []
								for item in temp_cases[index+1:]+temp_cases[:index]:
									consolidated.append(item['name'])
								temp_cases[index]['consolidated_with'] = consolidated

							cases = cases + temp_cases
							temp_cases = []
		#takes care of last case/group of consolidated cases
		if name != '': 
			if ')' in name:
				case['name'] = str(' '.join(name[1:].split()))
				temp_cases.append(case)
			else:
				case['name'] = str(' '.join(name.split()))
				case['consolidated_with'] = None
				cases.append(case)

		if temp_cases:
			for index in range(len(temp_cases)):
				consolidated = []
				for item in temp_cases[index+1:]+temp_cases[:index]:
					consolidated.append(item['name'])
				temp_cases[index]['consolidated_with'] = consolidated

			cases = cases + temp_cases
			temp_cases = []

		return cases

	def oct_thru_jan_parse_cases(self, response):
		box_xpath = '//*[@id="ctl00_ctl00_MainEditable_mainContent_RadEditor1"]/div/table/tr[2]/td/table/tr/td/table/tr/td'
		case = CaseItem()
		date = ''
		name = ''
		dockets = []
		links = []

		temp_cases = []
		cases = []
		consolidated = False

		for date_box in response.xpath(box_xpath):

			if date_box.xpath('p[2]/b/span/text()'):
				date = date_box.xpath('p[2]/b/span/text()').extract()[0].strip()
				date = ' '.join(date.split())
				date = str(date)

			for box in date_box.xpath('table/tr/td'):
				if box.xpath('.//a'): #we have reached a new link
					links = box.xpath('.//a/@href').extract() #collect all links in section
					dockets = box.xpath('.//a/span/text()').extract() #collect all dockets in section

					if box.xpath('.//p/span/text()'):
						if ')' in box.xpath('.//p/span/text()')[0].extract(): #case is consolidated
							consolidated = True
					else: #case stands alone
						consolidated = False
						if temp_cases: #no more cases to add to temp_cases, add to cases
							for index in range(len(temp_cases)):
								consolidated = []
								for item in temp_cases[index+1:]+temp_cases[:index]:
									consolidated.append(item['name'])
								temp_cases[index]['consolidated_with'] = consolidated

							cases = cases + temp_cases
							temp_cases = []
							consolidated = False


				elif box.xpath('.//p/span/text()'): #section has no link but has text, holds a name
					lines = box.xpath('.//p/span/text()').extract()
					
					if consolidated: 
					#use previously extracted links and dockets to construct case
					#dockets[0] corresponds to links[0] corresponds to lines[0]
						for line in lines:
							if links and dockets:
								name = str(' '.join(line.split()))
								case['date'] = date
								case['docket'] = str(dockets.pop(0))
								case['link'] = urljoin(response.url, str(links.pop(0)))
								
							elif name:
								name = name + ' ' + line
						#add case to array to be consolidated
						if name:
							case['name'] = name
							temp_cases.append(case)
							case = CaseItem()
							name = ''
							
					else: #not consolidated, construct cases 
						for line in lines: 
							if links and dockets:
								name = str(' '.join(line.split()))
								case['date'] = date
								case['docket'] = str(dockets.pop(0))
								case['link'] = urljoin(response.url, str(links.pop(0)))
								case['consolidated_with'] = None
							elif name: #must be a continuation of a name
								name = str(' '.join((name + ' ' + line).split()))
						#if case was created, add to result
						if name:
							case['name'] = name
							cases.append(case)
							case = CaseItem()
							name = ''
		#handles case if last case is consolidated
		if temp_cases:
			for index in range(len(temp_cases)):
				consolidated = []
				for item in temp_cases[index+1:]+temp_cases[:index]:
					consolidated.append(item['name'])
				temp_cases[index]['consolidated_with'] = consolidated

			cases = cases + temp_cases
			temp_cases = []

		return cases

