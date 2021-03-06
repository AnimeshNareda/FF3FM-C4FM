import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np
from sklearn.linear_model import LinearRegression


eps = 1e-6
r_f = 0.5


def checkifnan(num):
	if num is np.nan:
		return 0
	else:
		return num

# def find3factors(time_row):
	


df = pd.read_excel('CE_Europe.xlsx')
columns = list(df.loc[2])[1:]
# First five rows have no data
row_count = df.shape[0] - 5
companies = dict()
j = 0
company_name = ""
prev_err = False
for i,col in enumerate(columns):
	# Calculate the actual offset
	idx = i + 1
	if(col == "#ERROR"):
		prev_err = True
		j = (j+1)%3
		continue
	elif(j == 0):
		# New Company
		company_name = col.split('-')[0].strip()
		companies[company_name] = dict()
		# CAP
		a = np.nan_to_num(np.array(df.iloc[4:(4+row_count),idx]).astype(float))
		# print(a)
		companies[company_name]['CAP'] = a
		
	elif(j == 1):
		# ROI
		if(prev_err == True):
			company_name = col.split('-')[0].strip()
			if(company_name not in companies):
				companies[company_name] = dict()
		a = np.nan_to_num(np.array(df.iloc[4:(4+row_count),idx]).astype(float))
		companies[company_name]['ROI'] = a
	elif(j == 2):
		# PI
		if(prev_err == True):
			company_name = col.split('-')[0].strip()
			if(company_name not in companies):
				companies[company_name] = dict()
		a = np.nan_to_num(np.array(df.iloc[4:(4+row_count),idx]).astype(float))
		companies[company_name]['PI'] = a

	j = (j+1)%3
	prev_err = False
for company_name in companies:
	if 'PI' not in companies[company_name]:
		companies[company_name]['PI'] = np.array([0.]*row_count)
	if 'ROI' not in companies[company_name]:
		companies[company_name]['ROI'] = np.array([0.]*row_count)
	if 'CAP' not in companies[company_name]:
		# print(company_name)
		companies[company_name]['CAP'] = np.array([0.]*row_count)

marketcaparr = []
marketcap = []
priceindexarr = []
priceindex = []
growtharr = []
growth = []
booktomarketarr = []
booktomarket = []
companylist =[]

for company_name in companies:
	companylist.append(company_name)

three_factors = []

for x in range(row_count):
	for company_name in companies:
		marketcap.append(companies[company_name]['CAP'][x])
		priceindex.append(companies[company_name]['PI'][x])
		growth.append(companies[company_name]['ROI'][x])
		booktomarket.append(companies[company_name]['CAP'][x]/(companies[company_name]['PI'][x] + eps))
	marketcaparr.append(marketcap)
	priceindexarr.append(priceindex)
	growtharr.append(growth)
	booktomarketarr.append(booktomarket)
	high = np.percentile(booktomarket,70)
	low = np.percentile(booktomarket,30)
	small = np.percentile(marketcap,30)
	big = np.percentile(marketcap,70)
	valuefirm = []
	growthfirm = []
	neutralfirm = []
	smallfirm = []
	bigfirm = []
	for y in range(len(companylist)):
		if marketcap[y] > big:
			bigfirm.append(companylist[y])
		elif marketcap[y] < small:
			smallfirm.append(companylist[y])
		if booktomarket[y] < low:
			growthfirm.append(companylist[y])
		elif booktomarket[y] > low and booktomarket[y] < high:
			neutralfirm.append(companylist[y])
		elif booktomarket[y] > high:
			valuefirm.append(companylist[y])

	BV = list(set(bigfirm) & set(valuefirm))
	BN = list(set(bigfirm) & set(neutralfirm))
	BG = list(set(bigfirm) & set(growthfirm))
	SV = list(set(smallfirm) & set(valuefirm))
	SN = list(set(smallfirm) & set(neutralfirm))
	SG = list(set(smallfirm) & set(growthfirm))
	
	bvreturnarr = []
	bnreturnarr = []
	bgreturnarr = []
	svreturnarr = []
	snreturnarr = []
	sgreturnarr = []

	for company_name in BV:
		bvreturnarr.append(companies[company_name]['ROI'][x])
	for company_name in BN:
		bnreturnarr.append(companies[company_name]['ROI'][x])
	for company_name in BG:
		bgreturnarr.append(companies[company_name]['ROI'][x])
	for company_name in SV:
		svreturnarr.append(companies[company_name]['ROI'][x])
	for company_name in SN:
		snreturnarr.append(companies[company_name]['ROI'][x])
	for company_name in SG:
		sgreturnarr.append(companies[company_name]['ROI'][x])

	if len(bvreturnarr)> 0:
		bvreturn = np.average(bvreturnarr)
	else:
		bvreturn = 0

	if len(bnreturnarr)> 0:
		bnreturn = np.average(bnreturnarr)
	else:
		bnreturn = 0

	if len(bgreturnarr)> 0:
		bgreturn = np.average(bgreturnarr)
	else:
		bgreturn = 0


	if len(svreturnarr)> 0:
		svreturn = np.average(svreturnarr)
	else:
		svreturn = 0

	if len(snreturnarr)> 0:
		snreturn = np.average(snreturnarr)
	else:
		snreturn = 0

	if len(sgreturnarr)> 0:
		sgreturn = np.average(sgreturnarr)
	else:
		sgreturn = 0

	smb = (svreturn+snreturn+sgreturn)/3 - (bvreturn+bnreturn+bgreturn)/3 

	hml = (svreturn+bvreturn)/2 - (sgreturn+bgreturn)/2

	f = np.average(growth)
	three_factors.append([f-r_f,hml,smb])

# Now three_factors is a list of list
X = np.array(three_factors, np.float32)
# Xw = y regression
# Now apply linear regression for each company
for company_name in companies:
	y = companies[company_name]['ROI']
	y = y - r_f
	model = LinearRegression().fit(X, y)
	r_sq = model.score(X, y)
	print(company_name,model.coef_,r_sq)