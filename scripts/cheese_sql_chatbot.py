import os
import json
import sqlite3
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")

class CheeseSQLChatbot:
    def __init__(self, db_path: str = "./fixture/cheese_database.db"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.db_path = db_path
        self.conversation_history = []
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the SQLite database and create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            lb_price REAL,
            brand TEXT,
            upc TEXT,
            sku TEXT,
            weight REAL,
            product_url TEXT,
            image_url TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_data_from_json(self, json_file: str):
        """Load data from JSON file into SQLite database."""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM products")
        
        # Insert new data
        for product in data:
            cursor.execute('''
            INSERT INTO products (
                name, category, price, lb_price, brand, upc, sku, weight, product_url, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product.get('name'),
                product.get('category'),
                product.get('price'),
                product.get('LB_price'),
                product.get('brand'),
                product.get('UPC'),
                product.get('SKU'),
                product.get('weight'),
                product.get('product_url'),
                product.get('image_url')
            ))
        
        conn.commit()
        conn.close()
    
    def generate_sql_query(self, user_query: str) -> str:
        """Generate SQL query from natural language using GPT."""
        system_prompt = """You are a SQL query generator. Convert the user's question about cheese or cheese products into a valid SQL query.
        The database has a 'products' table with columns: name, category, price, lb_price, brand, upc, sku, weight.
        And cheese category can be 'Cheese Wheel', 'Cream Cheese', 'Crumbled, Cubed, Grated, Shaved','Sliced Cheese','Shredded Cheese', 'Cottage Cheese' or 'Cheese Loaf'.
        Return ONLY the SQL query without any explanation, markdown formatting, or backticks."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        response = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=150
        )
        
        # Clean up the SQL query by removing any markdown formatting or backticks
        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        print(sql_query)
        return sql_query
    
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            raise Exception(f"SQL Error: {str(e)}")
        finally:
            conn.close()
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format query results into a readable string."""
        if not results:
            return "No one"
        
        formatted_results = []
        for product in results:
            info = f"Product: {product['name']}\n"
            info += f"Category: {product['category']}\n"
            info += f"Price: ${product['price']}\n"
            if product['lb_price']:
                info += f"Price per pound: ${product['lb_price']}/lb\n"
            info += f"Brand: {product['brand']}\n"
            info += f"Product URL: {product['product_url']}\n"
            info += f"Image URL: {product['image_url']}\n"
            formatted_results.append(info)
        
        return "\n".join(formatted_results)
    
    def chat(self, query: str) -> str:
        """Main chat method that generates and executes SQL queries."""
        try:
            # Generate SQL query
            sql_query = self.generate_sql_query(query)
            
            # Execute query
            results = self.execute_query(sql_query)
            
            # Format results
            response = self.format_results(results)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
        except Exception as e:
            return f"I encountered an error: {str(e)}"

def main():
    # Initialize the chatbot
    chatbot = CheeseSQLChatbot()
    
    # Load data from JSON file
    chatbot.load_data_from_json("./fixture/cheese_data.json")
    
    print("Welcome to the Cheese Product SQL Assistant! Type 'quit' to exit.")
    print("Ask me anything about our cheese products!")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        response = chatbot.chat(user_input)
        print("\nAssistant:", response)

if __name__ == "__main__":
    main() 