from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")
web_address = "https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30#panel"
web_content = requests.get(web_address).text
web_content_soup = BeautifulSoup(web_content, "html.parser")

#find your right key here
table = soup.find('table', attrs={'class': 'table table-striped text-sm text-lg-normal'})
cek_row = table.find_all('tr')
row_length = len(cek_row)
table_ethereum = web_content_soup.find('table', attrs={'class': 'table table-striped text-sm text-lg-normal'})

list_ethereum = [] #initiating a list 

for table_rows in table_ethereum.find_all('tr'):
    # Find Header Date
    header_date = table_rows.find('th', attrs={'class': 'font-semibold text-center'})
    if(header_date) != None:
        periode = header_date.text.replace("-", "/")
        
    # Find record
    column_iteration = 0
    for table_columns in table_rows.find_all('td'):
        
        if (column_iteration) == 0:
            market_cap = table_columns.text.replace("$", "").replace(",", "").strip()
        elif (column_iteration) == 1:
            volume = table_columns.text.replace("$", "").replace(",", "").strip()
        elif (column_iteration) == 2:
            open_price = table_columns.text.replace("$", "").replace(",", "").strip()
        elif (column_iteration) == 3:
            close = table_columns.text.replace("$", "").replace(",", "").strip()
        
        if column_iteration == 3:
            list_ethereum.append((periode,market_cap, volume, open_price, close))
        
        column_iteration += 1

#change into dataframe
df_ethereum = pd.DataFrame(list_ethereum, columns = ('Periode','Market Cap','Volume', 'Open Price', 'Close'))

#insert data wrangling here
df_ethereum['Periode'] = df_ethereum['Periode'].astype('datetime64')
df_ethereum['Volume'] = df_ethereum['Volume'].astype('float64')
df_ethereum = df_ethereum.set_index('Periode')
df_ethereum['Volume'] = df_ethereum['Volume']

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df_ethereum["Volume"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df_ethereum.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)