# 🌐 Website Brochure Generator

An intelligent web scraper and AI-powered brochure generator that analyzes company websites and creates professional marketing brochures automatically.

## ✨ Features

- **Smart Web Scraping**: Extracts relevant content from company websites with robust error handling
- **AI-Powered Analysis**: Uses local LLMs (via Ollama) to identify important company pages and information
- **Automated Brochure Creation**: Generates professional markdown brochures with company overview, culture, products, and careers
- **Interactive User Interface**: Clean command-line interface with emoji indicators and progress updates
- **Multiple Output Options**: View in terminal or save as markdown files
- **Intelligent Link Detection**: Automatically identifies and processes relevant company pages (About, Careers, Products, etc.)
- **Connection Testing**: Validates URLs before processing to ensure reliability
- **Batch Processing**: Interactive mode for generating multiple brochures in one session

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running locally
- Required Python packages (see Installation)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/1morshed1/website-brochure-generator.git
cd website-brochure-generator
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_key_here" > .env
```

4. Start Ollama and pull the required model:

```bash
ollama pull llama3.2
```

### Usage

#### Single Brochure Generation

```bash
python brochure_generator.py
```

#### Interactive Mode (Multiple Brochures)

```bash
python brochure_generator.py --interactive
```

#### Example Session

```
============================================================
🌐 Website Brochure Generator
============================================================

Enter the website URL (e.g., https://example.com): huggingface.co
🔍 Testing connection to https://huggingface.co...

Enter the company name (or press Enter to auto-detect):
🤖 Auto-detected company name: Huggingface
Use 'Huggingface' as the company name? (y/n): y

🚀 Generating brochure for Huggingface...
This may take a few moments...

✅ Brochure generated successfully!

💾 Save brochure to file? (y/n): y
📄 Brochure saved to: huggingface_brochure.md
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Ollama Configuration

The script uses Ollama running locally on `http://localhost:11434`. Make sure you have:

1. Ollama installed and running
2. The `llama3.2` model pulled: `ollama pull llama3.2`

You can change the model by modifying the `MODEL` variable in the script.

## 🏗️ Architecture

### Core Components

1. **Website Class**: Handles web scraping with retry logic and error handling
2. **Link Extraction**: AI-powered identification of relevant company pages
3. **Content Processing**: Intelligent content extraction and cleaning
4. **Brochure Generation**: AI-powered markdown brochure creation
5. **User Interface**: Interactive command-line interface with validation

### Key Features

- **Robust Error Handling**: Handles network failures, DNS issues, and timeouts
- **Intelligent Content Filtering**: Removes irrelevant HTML elements and focuses on important content
- **URL Validation**: Ensures links are accessible before processing
- **Content Truncation**: Manages large content while preserving important information
- **Exponential Backoff**: Retry mechanism for failed requests

## 📊 Output Format

The generated brochures include:

- **Company Overview**: Mission, vision, and key information
- **Products/Services**: Main offerings and value propositions
- **Company Culture**: Values, team information, and work environment
- **Career Opportunities**: Available positions and company benefits
- **Market Position**: Target customers and industry standing

## 🔧 Customization

### Changing the AI Model

```python
MODEL = 'llama3.2'  # Change to your preferred model
```

### Modifying Brochure Style

Edit the `system_prompt` variable to change the brochure tone:

```python
# For a more humorous brochure
system_prompt = "You are an assistant that creates humorous, entertaining brochures..."
```

### Adjusting Content Limits

```python
# Change content truncation limit
details = details[:15000]  # Adjust character limit
```

## 🚨 Error Handling

The application handles various scenarios:

- **DNS Resolution Failures**: Retry with exponential backoff
- **Connection Timeouts**: Configurable timeout settings
- **Invalid URLs**: Input validation and user prompts
- **AI Processing Errors**: Graceful degradation and error reporting
- **File System Errors**: Safe file operations with error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM support
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [OpenAI](https://openai.com/) for API compatibility

## 📞 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/1morshed1/website-brochure-generator/issues) page
2. Review the error handling section above
3. Ensure Ollama is running and the model is downloaded
4. Verify your environment variables are set correctly

## 🔮 Future Enhancements

- [ ] Support for multiple output formats (PDF, HTML, Word)
- [ ] Integration with other LLM providers
- [ ] GUI interface using Streamlit or Gradio
- [ ] Batch processing from URL lists
- [ ] Custom brochure templates
- [ ] Multi-language support
- [ ] Integration with design tools for visual brochures

---

⭐ If you find this project helpful, please consider starring the repository!
