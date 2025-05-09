import requests  
from bs4 import BeautifulSoup 
import os

base_url = "https://shop.kimelo.com/department/cheese/3365"  
image_dir = "./images/"
total_data =[]



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
                data=[]
                # Extract data points for each cheese item  
                # Again, you'll need to inspect the HTML to find the right tags and classes  
                name = item.find('p', class_='chakra-text css-pbtft') # Replace 'product-name'  
                position = item.find('p', class_='chakra-text css-w6ttxb')
                price = item.find('b', class_='chakra-text css-1vhzs63') # Replace 'product-price'  
                LB_price =item.find('span', class_='chakra-badge css-ff7g47')
                # You might also look for descriptions, images, etc.  
                if name != None:
                    name=name.text.strip()
                else:
                    continue
                data.append(name)
                data.append(position.text.strip())
                if price != None:
                    data.append(price.text.strip())
                else:
                    data.append('')
                if LB_price != None:
                    data.append(LB_price.text.strip())
                else:
                    data.append('')

                # print(f"Cheese Name: {name}")  
                # print(f"position {position}")
                # print(f"Price: {price}")  
                # print(f"LB_price {LB_price}")
                
                image_tag = item.find('img')  

                if image_tag and 'src' in image_tag.attrs:  
                    image_url = image_tag['src']  
                    print()

                    # Construct the full image URL if it's a relative path  
                    if image_url.startswith('//'):  
                        image_url = 'http:' + image_url  
                    elif image_url.startswith('/'):  
                        # You might need to get the base domain from the original URL  
                        from urllib.parse import urljoin  
                        image_url = urljoin(url, image_url)  
                    data.append(image_url)
                total_data.append(data)
                # print(data)
                # print("-" * 20)  

                    
                   
        else:  
            print("Could not find any cheese items. The class name might be incorrect.")  

    except requests.exceptions.RequestException as e:  
        print(f"Error fetching the URL: {e}")  
    except Exception as e:  
        print(f"An error occurred: {e}")  


import json  

# Your Python list (array data)  

json_filename = "cheese_data.json"  

try:  
    with open(json_filename, 'w', encoding='utf-8') as f:  
        # json.dump() works directly with the list  
        json.dump(total_data, f, indent=4)  

    print(f"Successfully saved array data to {json_filename}")  

except IOError as e:  
    print(f"Error writing to JSON file: {e}")  