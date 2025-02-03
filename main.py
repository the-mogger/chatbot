import requests
from bs4 import BeautifulSoup
import streamlit as st 
import google.generativeai as genai
import logging
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="KL University ChatBot",
    page_icon="🎓",
    layout="wide"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)




# Cache the scraped content
@st.cache_data(ttl=3600)  # Cache for 1 hour
def scrape_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        text_content = []
        for tag in ['p', 'h1', 'h2', 'h3', 'article', 'section']:
            elements = soup.find_all(tag)
            text_content.extend([elem.get_text(strip=True) for elem in elements])
        
        return ' '.join(filter(None, text_content))
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return ""

def get_response(query, context=""):
    try:
        prompt = f"""Based on this context about KL University: {context}
        Question: {query}
        Please provide a clear, accurate, and helpful response. If the information is not in the context, say so."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "I apologize, but I couldn't generate a response at the moment. Please try again."

def main():
    st.title("🎓 KL University ChatBot")
    st.subheader("Ask me anything about KL University!")
    
    # URLs
    urls = [
        "https://www.kluniversity.in/",
        "https://www.kluniversity.in/about.aspx",
        "https://www.kluniversity.in/academics.aspx",
        "https://klh.edu.in/azadmissions/"
    ]
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    query = st.text_input("Your question:", key="user_input")
    
    if query:
        with st.spinner('Searching for information...'):
            # Scrape content from all URLs
            all_content = []
            for url in urls:
                content = scrape_content(url)
                if content:
                    all_content.append(content)
            
            combined_content = " ".join(all_content)
            
            # Get response
            response = get_response(query, combined_content)
            
            # Add to chat history
            st.session_state.chat_history.append({"query": query, "response": response})
    
    # Display chat history
    for chat in st.session_state.chat_history:
        st.write("🙋‍♂️ **You:** " + chat["query"])
        st.write("🤖 **Bot:** " + chat["response"])
        st.markdown("---")

if __name__ == "__main__":
    main()
