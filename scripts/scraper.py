import requests  
from bs4 import BeautifulSoup 
import os
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin  

base_url = "https://shop.kimelo.com/department/cheese/3365"  
total_data =[]
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
json_filename = "./fixture/cheese_data.json"  

# Create a driver instance
driver = webdriver.Chrome(options=chrome_options)

def extract_numbers_as_ints(text):
    number_strings = re.findall(r'-?\d+', text)
    return [int(num) for num in number_strings]

def extract_numbers_as_floats(text):
    number_strings = re.findall(r'-?\d+\.\d+|-?\d+', text)
    return [float(num) for num in number_strings]

for page_num in range(5):
    url = f"{base_url}?page={page_num+1}"
    # print(url)
    try:  
        response = requests.get(url)  
        response.raise_for_status()  # Raise an exception for bad status codes  

        soup = BeautifulSoup(response.content, 'html.parser')  

        # Find elements that contain cheese data  
        # This will likely involve inspecting the website's HTML structure  
        # using your browser's developer tools (F12).  
        # Look for common patterns like product names, prices, descriptions, etc.  

        # Example: Assuming cheese items are in div elements with a specific class  
        cheese_items = soup.find_all('div', class_='css-0') # Replace 'product-item' with the actual class  
        if cheese_items:  
            for item in cheese_items:  
                data={}
                # Extract data points for each cheese item  
                # Again, you'll need to inspect the HTML to find the right tags and classes  
                name = item.find('p', class_='chakra-text css-pbtft') # Replace 'product-name'  
                brand = item.find('p', class_='chakra-text css-w6ttxb')
                # You might also look for descriptions, images, etc.                  
               
                if name != None:
                    name=name.text.strip()
                else:
                    continue
                product_url = item.find('a', class_="chakra-card group css-5pmr4x").get('href')
                product_url = "https://shop.kimelo.com/" + product_url
                data["name"]=name
                data['brand']=brand.text.strip()
               
                data['product_url']=product_url

                # print(f"Cheese Name: {name}")  
                # print(f"position {position}")
                # print(f"Price: {price}")  
                # print(f"LB_price {LB_price}")
                
                image_tag = item.find('img')  

                if image_tag and 'src' in image_tag.attrs:  
                    image_url = image_tag['src']  

                    # Construct the full image URL if it's a relative path  
                    if image_url.startswith('//'):  
                        image_url = 'http:' + image_url  
                    elif image_url.startswith('/'):  
                        # You might need to get the base domain from the original URL  
                        image_url = urljoin(url, image_url)  
                    data['image_url']=image_url
                
                #detailed scraping
                print("detailed data")
                print(data['name'])
                # Navigate to the URL # Replace with your target URL
                driver.get(product_url)
                
                # Wait for the page to load (adjust as needed)
                time.sleep(3)
                
                # Get the page source after JavaScript execution
                html_content = driver.page_source
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                # Extract SKU & UPC number.
                numbers = soup.find_all('p', class_='chakra-text css-0')
                category = soup.find_all('a', class_='chakra-link chakra-breadcrumb__link css-1vtk5s8')
                
                if category[0].text.strip() == 'Cheese':
                    data['category']=category[1].text.strip()
                else:
                    data['category']=category[0].text.strip()
                    
                # print(data['category'])
                data['SKU_number']=extract_numbers_as_ints(numbers[0].text.strip())[0]
                data['UPC_number']=extract_numbers_as_ints(numbers[1].text.strip())[0]
                
                # Find the table
                table = soup.find('table', class_='chakra-table')
                # print("table_data")
                # Extract headers
                headers = []
                header_row = table.find('thead').find('tr')
                for th in header_row.find_all('th'):
                    headers.append(th.text.strip())
                
                # Extract table data
                rows = []
                for tr in table.find('tbody').find_all('tr'):
                    row_data = []
                    for td in tr.find_all('td'):
                        row_data.append(td.text.strip())
                    rows.append(row_data)
                data['table_data']=[headers,rows]
                data['weight']=rows[2][-1]
                data['weight']=extract_numbers_as_floats(data['weight'])[0]
                print(data['weight'])
                # Print results
                # print("Headers:", headers)
                # print("Data:")
                # for row in rows:
                #     print(row)
                
                like_products=soup.find('div', class_='col-span-2 css-0')
                # print(like_products)
                if like_products != None:
                    like_products=like_products.findAll('p', class_='chakra-text css-pbtft') 
                    # print("like_products:")
                    # print(like_products)
                    list=[]
                    for product in like_products:
                        list.append(product.text.strip())
                    like_products=list
                    # print(like_products)
                    data['like_products']=like_products
                else:
                    data['like_products']=[]
                print("prices")
                prices=soup.find('div', class_='relative shadow-md border rounded-lg p-4 sticky top-[100px] css-1811skr').findAll('div', class_='css-1ktp5rg')
                LB_price=soup.find('div', class_='relative shadow-md border rounded-lg p-4 sticky top-[100px] css-1811skr').find('span', class_='chakra-badge css-1mwp5d1')
                i=0
                for price in prices:
                    price=price.find('b', class_='chakra-text css-0').text.strip()
                    price=extract_numbers_as_floats(price)[0]
                    prices[i]=price
                    i+=1
                print(prices)
                if len(prices) == 2:
                    if prices[0] > prices[1]:
                        data['price']=prices[1]
                        data['case_price']=prices[0]
                    else:
                        data['price']=prices[0]
                        data['case_price']=prices[1]
                    case_size=extract_numbers_as_ints(data['table_data'][1][0][0])
                    data['case_size']=case_size[0]
                    print(case_size)
                else:
                    data['price']=prices[0]
                    data['case_size']=1
                    data['case_price']=prices[0]
                print(data['price'])
                print(data['case_price'])
                if LB_price != None:
                    data['LB_price']=LB_price.text.strip()
                    data['LB_price']=extract_numbers_as_floats(data['LB_price'])[0]
                else:
                    data['LB_price']=0
                # print("related_products")
                # print(related_products)
                
                related_products=soup.find('div', class_='relative shadow-md border rounded-lg p-4 sticky top-[100px] css-1811skr').findAll('div', class_='relative css-1bpq4gx')
                list=[]
                for product in related_products:
                    temp=product.find('p', class_='chakra-text css-pbtft')
                    temp=temp.text.strip()
                    list.append(temp)
                related_products=list
                data['related_products']=related_products

                list=[]
                product_images=soup.find('div', class_='chakra-tabs__tablist mt-2 css-wjy2tx').findAll('img')
                for image in product_images:
                    list.append(urljoin(url, image['src']))
                product_images=list
                data['product_images']=product_images
                # print(data)
                total_data.append(data)

        else:  
            print("Could not find any cheese items. The class name might be incorrect.");

    except requests.exceptions.RequestException as e:  
        print(f"Error fetching the URL: {e}")  
    except Exception as e:  
        print(f"An error occurred: {e}")  

driver.quit()
import json  

# Your Python list (array data)  


try:  
    with open(json_filename, 'w', encoding='utf-8') as f:  
        # json.dump() works directly with the list  
        json.dump(total_data, f, indent=4)  

    print(f"Successfully saved array data to {json_filename}")  

except IOError as e:  
    print(f"Error writing to JSON file: {e}")  