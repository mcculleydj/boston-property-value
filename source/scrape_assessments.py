import requests
import re
import json
import time
import pymongo
import bs4

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected')

asmts_2016 = client.repo.asmts_2016
parcels = client.repo.parcels
missing_parcels = client.repo.missing_parcels
failed_parcels = client.repo.failed_parcels

# a method to clean up addresses for geocoding

SUFFIXES = {'AV',
			'BL',
			'CC',
			'CI',
			'CR',
			'CW',
			'CT',
			'DR',
			'HW',
			'LA',
			'LN',
			'PK',
			'PL',
			'PW',
			'PZ',
			'RD',
			'RO',
			'SQ',
			'ST',
			'TE',
			'WA',
			'WY',
			'WH'}

# standalone street names that do not have
# a suffix in Boston

NO_SUFFIX = {'FENWAY',
		     'JAMAICAWAY'}

def refine_address(raw_address):
	tokens = raw_address.split()
	filter_on = False
	filtered_tokens = []
	suffix_not_found = True
	invalid_address = True
	for token in tokens:
		if token in SUFFIXES:
			filter_on = True
			suffix_not_found = False
			invalid_address = False
			filtered_tokens.append(token)
		if token == 'BOSTON':
			filter_on = False
		if not filter_on:
			filtered_tokens.append(token)
	if suffix_not_found:
		filtered_tokens = []
		for token in tokens:
			if token in NO_SUFFIX:
				filter_on = True
				filtered_tokens.append(token)
				invalid_address = False
			if token == 'BOSTON':
				filter_on = False
			if not filter_on:
				filtered_tokens.append(token)
	if invalid_address:
		print ('Raw address string is invalid:', raw_address)
		return ''
	return ' '.join(token for token in filtered_tokens)

print('Scraping assessment data on each PID...')

START = 0
index = START + 1

documents = asmts_2016.find(no_cursor_timeout=True).skip(START)

# to retry scraping the parcels that did not succeed
# uncomment the following line
# documents = failed_parcels.find()

count = documents.count()

for d in documents:

	url = 'http://www.cityofboston.gov/assessing/search/?pid=' + d['pid']

	try:
		result = requests.get(url)
	except Exception as e:
		print('Exception:', e)
		print('Scrape failed; inserting parcel with PID',
			  d['pid'], 'into failed_parcels...')
		failed_parcels.insert_one(d)
		index += 1
		time.sleep(3)
		continue
	
	soup = bs4.BeautifulSoup(result.content, 'html.parser')
	
	# not every pid in asmts_2016 has retrievable assessment data:
	result_set_main = soup.find_all('div', class_='mainLeadStory')
	is_avail = (3 != len(result_set_main[0].contents))

	if not is_avail:
		print('Data not available; inserting parcel with PID',
			  d['pid'], 'into missing_parcels...')
		missing_parcels.insert_one(d)
		index += 1
		time.sleep(.1)
		continue

	result_set_center = soup.find_all('td', align='center')
	result_set_right = soup.find_all('td', align='right')

	d['history'] = {}

	# result_set_center
	for r in result_set_center:
		c = r.contents
		if c[0].isdigit():
			year = c[0]
			d['history'][year] = {}
		if c[0][0] == '$':
			d['history'][year]['value'] = int(re.sub(r'\D', '', c[0])) // 100
		else:
			if c[0][-1] == ' ':							# remove trailing whitespace
				d['history'][year]['type'] = c[0][:-1]
			else:
				d['history'][year]['type'] = c[0]

	# result_set_right
	address_raw = result_set_right[2].get_text()
	address = refine_address(address_raw)				# refine for geocoding
	
	if not address:
		print('Address refinement failed; inserting parcel with PID',
		      d['pid'], 'into failed_parcels...')	
		failed_parcels.insert_one(d)
		index += 1
		time.sleep(.1)
		continue

	p_type = result_set_right[3].get_text()
	
	p_code = result_set_right[4].get_text()
	
	lot_size_raw = result_set_right[5].get_text()
	lot_size = int(re.sub(r'\D', '', lot_size_raw))
	
	living_area_raw = result_set_right[6].get_text()
	living_area = int(re.sub(r'\D', '', living_area_raw))
	
	curr_owner_raw = result_set_right[7].get_text()
	curr_owner = re.sub(r'\s+', ' ', curr_owner_raw)
	if curr_owner[0] == ' ': curr_owner = curr_owner[1:]
	if curr_owner[-1] == ' ': curr_owner = curr_owner[:-1]
	
	curr_owner_addr_raw = result_set_right[8].get_text()
	curr_owner_addr = re.sub(r'\s+', ' ', curr_owner_addr_raw)
	if curr_owner_addr[0] == ' ': curr_owner = curr_owner[1:]
	if curr_owner_addr[-1] == ' ': curr_owner = curr_owner[:-1]

	res_exempt = result_set_right[9].get_text()
	
	pers_exempt = result_set_right[10].get_text()
	
	bldg_val_raw = result_set_right[11].get_text()
	bldg_val = int(re.sub(r'\D', '', bldg_val_raw)) // 100
	
	land_val_raw = result_set_right[12].get_text()
	land_val = int(re.sub(r'\D', '', land_val_raw)) // 100
	
	res_tax_rate_raw = result_set_right[14].get_text()
	res_tax_rate = float(re.sub(r'\D', '', res_tax_rate_raw)) / 100
	
	com_tax_rate_raw = result_set_right[15].get_text()
	com_tax_rate = float(re.sub(r'\D', '', com_tax_rate_raw)) / 100
	
	gross_tax_raw = result_set_right[16].get_text()
	gross_tax = float(re.sub(r'\D', '', gross_tax_raw)) / 100

	res_exmp_amt_raw = result_set_right[17].get_text()
	res_exmp_amt = float(re.sub(r'\D', '', res_exmp_amt_raw)) / 100	

	pers_exmp_amt_raw = result_set_right[18].get_text()
	pers_exmp_amt = float(re.sub(r'\D', '', pers_exmp_amt_raw)) / 100

	net_tax_raw = result_set_right[19].get_text()
	net_tax = float(re.sub(r'\D', '', net_tax_raw)) / 100	

	d['address'] = address
	d['p_type'] = p_type
	d['p_code'] = p_code
	d['lot_size'] = lot_size
	d['living_area'] = living_area
	d['curr_owner'] = curr_owner
	d['curr_owner_addr'] = curr_owner_addr
	d['res_exempt'] = res_exempt
	d['pers_exempt'] = pers_exempt
	d['bldg_val'] = bldg_val
	d['land_val'] = land_val
	d['res_tax_rate'] = res_tax_rate
	d['com_tax_rate'] = com_tax_rate
	d['gross_tax'] = gross_tax
	d['res_exmp_amt'] = res_exmp_amt
	d['pers_exmp_amt'] = pers_exmp_amt
	d['net_tax'] = net_tax

	parcels.insert_one(d)

	print('Scrape successful; inserting parcel with PID', d['pid'] ,'into parcels.')
	print('Completed %d of %d parcels...' % (index, count))
	
	index += 1
	time.sleep(.1) # shorter durations may induce server errors

documents.close()

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF
