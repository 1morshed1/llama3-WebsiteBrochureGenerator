# imports
import os
import requests
import json
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI
from urllib.parse import urljoin, urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize and constants
MODEL = 'llama3.2'
openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# Enhanced headers with more realistic user agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

class Website:
    """
    A utility class to represent a Website that we have scraped, with improved error handling
    """

    def __init__(self, url: str, timeout: int = 10, max_retries: int = 3):
        self.url = url
        self.title = "No title found"
        self.text = ""
        self.links = []
        self.success = False
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to fetch {url} (attempt {attempt + 1}/{max_retries})")
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                self.body = response.content
                soup = BeautifulSoup(self.body, 'html.parser')
                
                # Extract title
                if soup.title:
                    self.title = soup.title.string.strip()
                
                # Extract text content
                if soup.body:
                    # Remove irrelevant elements
                    for irrelevant in soup.body(["script", "style", "img", "input", "nav", "footer", "header"]):
                        irrelevant.decompose()
                    self.text = soup.body.get_text(separator="\n", strip=True)
                    # Clean up excessive whitespace
                    self.text = '\n'.join(line.strip() for line in self.text.split('\n') if line.strip())
                
                # Extract and normalize links
                links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href:
                        # Convert relative URLs to absolute URLs
                        absolute_url = urljoin(url, href)
                        # Only include HTTP/HTTPS links
                        if absolute_url.startswith(('http://', 'https://')):
                            links.append(absolute_url)
                
                self.links = list(set(links))  # Remove duplicates
                self.success = True
                logger.info(f"Successfully fetched {url}")
                break
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    self.text = f"Failed to fetch content from {url}: {str(e)}"

    def get_contents(self) -> str:
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

# Improved link system prompt
link_system_prompt = """You are provided with a list of links found on a webpage. 
You are able to decide which of the links would be most relevant to include in a brochure about the company, 
such as links to an About page, Company page, Careers/Jobs pages, Products/Services pages, or Team pages.

You should respond in JSON format with only the most relevant links (maximum 5 links).
Example response:
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"},
        {"type": "products page", "url": "https://example.com/products"}
    ]
}

Important: Only include links that are clearly relevant for a company brochure. 
Exclude: Terms of Service, Privacy Policy, Contact forms, Social media links, Blog posts, Documentation."""

def get_links_user_prompt(website: Website) -> str:
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company. "
    user_prompt += "Respond with the full https URL in JSON format. Select only the most important links (max 5).\n\n"
    user_prompt += "Links:\n"
    user_prompt += "\n".join(website.links[:50])  # Limit to first 50 links to avoid token limits
    return user_prompt

def get_links(url: str) -> Dict:
    """Extract relevant links from a website with error handling"""
    website = Website(url)
    
    if not website.success:
        logger.error(f"Failed to fetch website {url}")
        return {"links": []}
    
    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": link_system_prompt},
                {"role": "user", "content": get_links_user_prompt(website)}
            ],
            response_format={"type": "json_object"},
            temperature=0.1  # Lower temperature for more consistent JSON output
        )
        result = response.choices[0].message.content
        parsed_result = json.loads(result)
        
        # Validate that links are accessible
        validated_links = []
        for link in parsed_result.get("links", []):
            if validate_url(link.get("url", "")):
                validated_links.append(link)
        
        return {"links": validated_links}
        
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error processing links for {url}: {e}")
        return {"links": []}

def validate_url(url: str) -> bool:
    """Validate if a URL is accessible"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Quick head request to check if URL is accessible
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        return response.status_code < 400
    except:
        return False

def get_all_details(url: str) -> str:
    """Get website details with improved error handling and content management"""
    result = "Landing page:\n"
    main_website = Website(url)
    result += main_website.get_contents()
    
    if not main_website.success:
        return result
    
    links = get_links(url)
    logger.info(f"Found {len(links['links'])} relevant links")
    
    for link in links["links"]:
        try:
            link_url = link["url"]
            logger.info(f"Processing {link['type']}: {link_url}")
            
            link_website = Website(link_url)
            if link_website.success:
                result += f"\n\n{link['type'].title()}:\n"
                result += link_website.get_contents()
            else:
                logger.warning(f"Failed to fetch {link_url}")
                
        except Exception as e:
            logger.error(f"Error processing link {link}: {e}")
            continue
    
    return result

# Improved system prompt
system_prompt = """You are an assistant that analyzes the contents of several relevant pages from a company website 
and creates a comprehensive yet concise brochure about the company for prospective customers, investors and recruits. 

Your brochure should be well-structured and include:
- Company overview and mission
- Key products/services
- Company culture and values
- Career opportunities (if available)
- Target customers and market position

Respond in clean, professional markdown format. Make the brochure engaging and informative while keeping it concise."""

def get_brochure_user_prompt(company_name: str, url: str) -> str:
    """Generate user prompt with content length management"""
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a comprehensive brochure of the company in markdown.\n\n"
    
    details = get_all_details(url)
    
    # Intelligent truncation - keep the most important parts
    if len(details) > 15000:
        lines = details.split('\n')
        truncated_lines = []
        char_count = 0
        
        for line in lines:
            if char_count + len(line) > 15000:
                truncated_lines.append("... (content truncated for length)")
                break
            truncated_lines.append(line)
            char_count += len(line)
        
        details = '\n'.join(truncated_lines)
    
    user_prompt += details
    return user_prompt

def create_brochure(company_name: str, url: str) -> Optional[str]:
    """Create brochure with error handling"""
    try:
        logger.info(f"Creating brochure for {company_name} at {url}")
        
        user_prompt = get_brochure_user_prompt(company_name, url)
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        display(Markdown(result))
        return result
        
    except Exception as e:
        logger.error(f"Error creating brochure: {e}")
        error_msg = f"# Error Creating Brochure\n\nFailed to create brochure for {company_name}: {str(e)}"
        display(Markdown(error_msg))
        return None

def get_user_input():
    """Get website URL and company name from user input"""
    print("=" * 60)
    print("🌐 Website Brochure Generator")
    print("=" * 60)
    
    while True:
        url = input("\nEnter the website URL (e.g., https://example.com): ").strip()
        
        if not url:
            print("❌ Please enter a valid URL")
            continue
            
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                print("❌ Invalid URL format. Please try again.")
                continue
        except Exception:
            print("❌ Invalid URL format. Please try again.")
            continue
            
        # Test if URL is accessible
        try:
            print(f"🔍 Testing connection to {url}...")
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code >= 400:
                print(f"⚠️  Website returned status code {response.status_code}")
                retry = input("Continue anyway? (y/n): ").lower()
                if retry != 'y':
                    continue
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to {url}")
            print(f"Error: {e}")
            retry = input("Try a different URL? (y/n): ").lower()
            if retry != 'y':
                return None, None
            continue
            
        break
    
    # Get company name
    while True:
        company_name = input(f"\nEnter the company name (or press Enter to auto-detect): ").strip()
        
        if not company_name:
            # Try to auto-detect from URL
            domain = urlparse(url).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            company_name = domain.split('.')[0].title()
            print(f"🤖 Auto-detected company name: {company_name}")
            
        confirm = input(f"Use '{company_name}' as the company name? (y/n): ").lower()
        if confirm == 'y':
            break
            
    return url, company_name

def main():
    """Main function to run the brochure generator"""
    try:
        url, company_name = get_user_input()
        
        if not url or not company_name:
            print("👋 Goodbye!")
            return
            
        print(f"\n🚀 Generating brochure for {company_name}...")
        print("This may take a few moments...")
        
        result = create_brochure(company_name, url)
        
        if result:
            print(f"\n✅ Brochure generated successfully!")
            
            # Ask if user wants to save to file
            save = input("\n💾 Save brochure to file? (y/n): ").lower()
            if save == 'y':
                filename = f"{company_name.lower().replace(' ', '_')}_brochure.md"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"📄 Brochure saved to: {filename}")
                except Exception as e:
                    print(f"❌ Error saving file: {e}")
        else:
            print("❌ Failed to generate brochure")
            
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        logger.error(f"Unexpected error in main: {e}")

def interactive_mode():
    """Interactive mode allowing multiple brochure generations"""
    print("🎯 Interactive Mode - Generate multiple brochures")
    
    while True:
        main()
        
        print("\n" + "=" * 60)
        another = input("Generate another brochure? (y/n): ").lower()
        if another != 'y':
            break
    
    print("👋 Thank you for using the Website Brochure Generator!")

# Example usage with user input
if __name__ == "__main__":
    try:
        # Check if running interactively
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
            interactive_mode()
        else:
            main()
    except Exception as e:
        print(f"Error in main execution: {e}")
        logger.error(f"Fatal error: {e}")
