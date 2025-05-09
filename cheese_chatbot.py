import os
from typing import List, Dict, Any
from openai import OpenAI
from pinecone import Pinecone
import json
from cheese_sql_chatbot import CheeseSQLChatbot

from dotenv import load_dotenv
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHAT_MODEL = os.getenv("CHAT_MODEL")
prompt_filename = "prompt.txt"

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

class FoodChatbot:
    def __init__(self):
        self.index = pc.Index(INDEX_NAME)
        self.conversation_history = []
        
    def get_relevant_products(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant products from Pinecone based on the query."""
        # Generate embedding for the query
        query_embedding = client.embeddings.create(
            input=query,
            model=EMBEDDING_MODEL
        ).data[0].embedding
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        return results.matches
    
    def format_product_info(self, products: List[Dict[str, Any]]) -> str:
        """Format product information for the context."""
        formatted_info = []
        for product in products:
            info = f"Product: {product.metadata.get('name', 'N/A')}\n"
            info += f"Category: {product.metadata.get('category', 'N/A')}\n"
            info += f"Price: ${product.metadata.get('price', 'N/A')}\n"
            if product.metadata.get('LB_price'):
                info += f"Price per pound: ${product.metadata.get('LB_price')}/lb\n"
            info += f"Brand: {product.metadata.get('brand', 'N/A')}\n"
            info += f"Similarity Score: {product.score:.2f}\n"
            info += f"Product URL: {product.metadata.get('product_url', 'N/A')}\n"
            info += f"image_url: {product.metadata.get('image_url', 'N/A')}\n"
            info += f"UPC: {product.metadata.get('UPC', 'N/A')}\n"
            info += f"SKU: {product.metadata.get('SKU', 'N/A')}\n"
            info += f"Related Products: {product.metadata.get('related_products', 'N/A')}\n"
            formatted_info.append(info)
        
        return "\n".join(formatted_info)
    
    def format_conversation_history(self) -> str:
        """Format the conversation history for context."""
        if not self.conversation_history:
            return ""
        
        formatted_history = "Previous conversation:\n"
        for message in self.conversation_history[-5:]:  # Only include last 5 exchanges
            formatted_history += f"{message['role']}: {message['content']}\n"
        return formatted_history
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate a response using GPT-4 with the retrieved context."""
        # system_prompt = """You are a helpful food product assistant. Use the provided product information 
        # to answer questions about food products. Be concise, accurate, and helpful. If you don't have 
        # enough information to answer a question, say 'I'm sorry, I don't have enough information on that product.'."""
        with open(prompt_filename, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        conversation_history = self.format_conversation_history()
        full_context = f"{conversation_history}\n\nCurrent Product Information:\n{context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{full_context}\n\nQuestion: {query}"}
        ]
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def chat(self, query: str) -> str:
        """Main chat method that combines retrieval and generation."""
        # Get relevant products
        relevant_products = self.get_relevant_products(query)
        # Format product information
        context = self.format_product_info(relevant_products)


        # Generate SQL query
        sql_chatbot = CheeseSQLChatbot()
        sql_response = sql_chatbot.chat(query)
        print("sql")
        
        if sql_response != "No one":
            print(sql_response)
            context = sql_response
        # Generate response
        response = self.generate_response(query, context)
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep only last 10 exchanges
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return response
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

def main():
    # Initialize the chatbot
    chatbot = FoodChatbot()
    
    print("Welcome to the Food Product Assistant! Type 'quit' to exit.")
    print("Ask me anything about our food products!")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        try:
            response = chatbot.chat(user_input)
            print("\nAssistant:", response)
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("I apologize, but I encountered an error. Please try again.")

if __name__ == "__main__":
    main()