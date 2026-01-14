# Research Agent - Tool Registry
# This module manages all search tools available to the agent

import os
import logging
from tavily import TavilyClient
from langchain_core.tools import tool
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import ArxivLoader
from langchain_community.document_loaders import PubMedLoader
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging - only to file, not console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log', mode='a', encoding='utf-8')
    ]
)
logging = logging.getLogger(__name__)


@tool
def tavily_search(query: str) -> str:
    """
    Search the internet using Tavily API to find relevant URLs.
    Returns top 3 URLs by relevance score. Use fetch_url_content to read the full content from these URLs.
    
    Args:
        query: The search query string
        
    Returns:
        str: Top 3 URLs with titles and scores
    """
    logging.info(f"TOOL: tavily_search | INPUT: {query}")
    
    api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key:
        result = "Error: TAVILY_API_KEY environment variable is not set"
        logging.info(f"TOOL: tavily_search | OUTPUT: {result}")
        return result
    
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=10)
        
        results = response.get("results", [])
        
        if not results:
            result = "No results found."
            logging.info(f"TOOL: tavily_search | OUTPUT: {result}")
            return result
        
        # Sort by score and get top 3
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        top_3 = sorted_results[:3]
        
        # Format only title and URL for top 3
        formatted = []
        for i, res in enumerate(top_3, 1):
            formatted.append(
                f"{i}. {res.get('title', 'No title')}\n"
                f"   URL: {res.get('url', 'No URL')}\n"
                f"   Score: {res.get('score', 'N/A')}"
            )
        
        result = "\n\n".join(formatted)
        result += "\n\nUse fetch_url_content tool to read the full content from these URLs."
        
        logging.info(f"TOOL: tavily_search | OUTPUT: Top 3 URLs from {len(results)} results")
        return result
        
    except Exception as e:
        result = f"Tavily search failed: {str(e)}"
        logging.info(f"TOOL: tavily_search | OUTPUT: {result}")
        return result


@tool
def fetch_url_content(url: str) -> str:
    """
    Fetch and parse the full content from a web page URL.
    Use this when you need to read detailed information from a specific webpage.
    
    Args:
        url: The web page URL to fetch content from
        
    Returns:
        str: The parsed text content from the webpage
    """
    logging.info(f"TOOL: fetch_url_content | INPUT: {url}")
    
    try:
        loader = UnstructuredURLLoader(urls=[url])
        docs = loader.load()
        
        if not docs:
            result = f"No content found at {url}"
            logging.info(f"TOOL: fetch_url_content | OUTPUT: {result}")
            return result
        
        content = docs[0].page_content
        
        # Limit content length to avoid token limits
        max_length = 3000
        if len(content) > max_length:
            content = content[:max_length] + "...\n[Content truncated]"
        
        result = f"Content from {url}:\n\n{content}"
        logging.info(f"TOOL: fetch_url_content | OUTPUT: Fetched {len(content)} chars")
        return result
        
    except Exception as e:
        result = f"Failed to fetch content from {url}: {str(e)}"
        logging.info(f"TOOL: fetch_url_content | OUTPUT: {result}")
        return result


@tool
def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for comprehensive, reliable general knowledge on any topic.
    
    Best for: Definitions, concepts, historical facts, biographies, general information.
    Returns detailed content from top Wikipedia articles with metadata.
    
    Args:
        query: The topic or concept to search for on Wikipedia
    
    Returns:
        str: Wikipedia article content with title, summary, and source URL
    """
    logging.info(f"TOOL: wikipedia_search | INPUT: {query}")
    
    try:
        # Load Wikipedia documents
        loader = WikipediaLoader(
            query=query,
            load_max_docs=2,  # Load top 2 articles
            doc_content_chars_max=4000,  # Max 4000 chars per article
            load_all_available_meta=True  # Get all metadata
        )
        
        docs = loader.load()
        
        if not docs:
            return f"No Wikipedia articles found for query: {query}"
        
        # Format the results
        result_parts = []
        for i, doc in enumerate(docs, 1):
            result_parts.append(f"--- Article {i}: {doc.metadata.get('title', 'Unknown')} ---")
            result_parts.append(f"Source: {doc.metadata.get('source', 'N/A')}")
            result_parts.append(f"\nContent:\n{doc.page_content}\n")
        
        result = "\n".join(result_parts)
        
        logging.info(f"TOOL: wikipedia_search | OUTPUT: Found {len(docs)} articles, total length: {len(result)} chars")
        return result
        
    except Exception as e:
        error_msg = f"Error searching Wikipedia: {str(e)}"
        logging.error(f"TOOL: wikipedia_search | ERROR: {error_msg}")
        return error_msg


@tool
def arxiv_search(query: str) -> str:
    """
    Search arXiv for academic research papers and scientific publications.
    
    Best for: Recent research, academic papers, scientific findings, technical topics.
    Returns paper abstracts, authors, publication dates, and summaries.
    
    Args:
        query: Research topic, paper title, or scientific concept to search for
    
    Returns:
        str: Research paper details including titles, authors, summaries, and publication info
    """
    logging.info(f"TOOL: arxiv_search | INPUT: {query}")
    
    try:
        # Initialize ArxivLoader
        loader = ArxivLoader(
            query=query,
            load_max_docs=3  # Load top 3 papers
        )
        
        # Get summaries as documents (faster, no full PDF download)
        docs = loader.get_summaries_as_docs()
        
        if not docs:
            return f"No arXiv papers found for query: {query}"
        
        # Format the results
        result_parts = []
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            result_parts.append(f"\n--- Paper {i} ---")
            result_parts.append(f"Title: {metadata.get('Title', 'N/A')}")
            result_parts.append(f"Authors: {metadata.get('Authors', 'N/A')}")
            result_parts.append(f"Published: {metadata.get('Published', 'N/A')}")
            result_parts.append(f"Entry ID: {metadata.get('Entry ID', 'N/A')}")
            result_parts.append(f"\nAbstract:\n{doc.page_content}")
            result_parts.append("\n" + "="*50)
        
        result = "\n".join(result_parts)
        
        logging.info(f"TOOL: arxiv_search | OUTPUT: Found {len(docs)} papers")
        return result
        
    except Exception as e:
        error_msg = f"Error searching arXiv: {str(e)}"
        logging.error(f"TOOL: arxiv_search | ERROR: {error_msg}")
        return error_msg


@tool
def youtube_transcript(video_url: str) -> str:
    """
    Extract transcript and information from a YouTube video.
    
    Best for: Getting transcripts, video summaries, and content from YouTube videos.
    Supports videos with captions/subtitles. Returns full transcript text.
    
    Args:
        video_url: Full YouTube video URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
    
    Returns:
        str: Video transcript with title and basic information
    """
    logging.info(f"TOOL: youtube_transcript | INPUT: {video_url}")
    
    try:
        # Initialize YoutubeLoader with video info
        loader = YoutubeLoader.from_youtube_url(
            video_url,
            add_video_info=True,
            language=["en", "hi"]  # Support English and Hindi
        )
        
        # Load the document
        docs = loader.load()
        
        if not docs:
            return f"Could not load transcript from: {video_url}. Video may not have captions available."
        
        # Get the document
        doc = docs[0]
        
        # Format the result
        result_parts = [
            f"=== YouTube Video Transcript ===",
            f"URL: {video_url}",
            f"\nTranscript:\n",
            doc.page_content
        ]
        
        result = "\n".join(result_parts)
        
        logging.info(f"TOOL: youtube_transcript | OUTPUT: Loaded transcript (length: {len(doc.page_content)} chars)")
        return result
        
    except Exception as e:
        error_msg = f"Error loading YouTube transcript: {str(e)}. Make sure the video has captions/subtitles available."
        logging.error(f"TOOL: youtube_transcript | ERROR: {error_msg}")
        return error_msg


@tool
def pubmed_search(query: str, max_results: int = 3) -> str:
    """
    Search PubMed for biomedical and medical research articles.
    
    Best for: Medical research, health topics, clinical studies, drug information,
    disease research, biological sciences, healthcare topics.
    
    Args:
        query: Medical or scientific topic to search (e.g., "diabetes treatment", "COVID-19 vaccines")
        max_results: Number of articles to return (default: 3, max recommended: 10)
    
    Returns:
        str: Research articles with titles, abstracts, authors, and publication info
    """
    logging.info(f"TOOL: pubmed_search | INPUT: {query}, max_results={max_results}")
    
    try:
        # Initialize PubMed loader
        loader = PubMedLoader(query, load_max_docs=max_results)
        
        # Load documents
        docs = loader.load()
        
        if not docs:
            return f"No PubMed articles found for: {query}"
        
        # Format results
        result_parts = [
            f"=== PubMed Search Results ===",
            f"Query: {query}",
            f"Found: {len(docs)} articles\n"
        ]
        
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            result_parts.append(f"\n--- Article {i} ---")
            result_parts.append(f"Title: {metadata.get('Title', 'N/A')}")
            result_parts.append(f"Published: {metadata.get('Published', 'N/A')}")
            result_parts.append(f"PubMed ID: {metadata.get('uid', 'N/A')}")
            
            # Add authors if available
            if 'Authors' in metadata:
                authors = metadata['Authors'][:3]  # First 3 authors
                result_parts.append(f"Authors: {', '.join(authors)}")
            
            result_parts.append(f"\nAbstract:\n{doc.page_content[:1000]}...")  # First 1000 chars
            result_parts.append(f"\n{'='*50}")
        
        result = "\n".join(result_parts)
        
        logging.info(f"TOOL: pubmed_search | OUTPUT: Found {len(docs)} articles")
        return result
        
    except Exception as e:
        error_msg = f"Error searching PubMed: {str(e)}"
        logging.error(f"TOOL: pubmed_search | ERROR: {error_msg}")
        return error_msg


@tool
def pdf_extract(file_path: str) -> str:
    """
    Extract text, tables, and structure from PDF documents (research papers, articles).
    
    Optimized for academic papers - preserves formatting, extracts tables as markdown,
    and maintains document structure. Works with local files and URLs.
    
    Args:
        file_path: Path to PDF file (local path like './paper.pdf' or URL starting with http/https)
    
    Returns:
        str: Extracted content in markdown format with metadata (title, author, pages)
    """
    logging.info(f"TOOL: pdf_extract | INPUT: {file_path}")
    
    try:
        # Initialize PyMuPDF4LLM loader
        loader = PyMuPDF4LLMLoader(
            file_path,
            mode="page",  # Split by page for better structure
            extract_images=False  # Skip images for speed (can enable if needed)
        )
        
        # Load documents
        docs = loader.load()
        
        if not docs:
            return f"Could not extract content from PDF: {file_path}"
        
        # Get metadata from first document
        metadata = docs[0].metadata
        
        # Format results
        result_parts = [
            "=== PDF Content Extraction ===",
            f"Source: {metadata.get('source', 'N/A')}",
            f"Total Pages: {metadata.get('total_pages', len(docs))}",
            f"Format: {metadata.get('format', 'N/A')}",
            f"Created: {metadata.get('creationdate', 'N/A')}",
            f"Producer: {metadata.get('producer', 'N/A')}",
            f"\n{'='*50}\n"
        ]
        
        # Add content from each page
        for doc in docs:
            page_num = doc.metadata.get('page', 'Unknown')
            result_parts.append(f"\n--- Page {page_num + 1} ---\n")
            
            # Limit content per page to avoid token limits
            content = doc.page_content
            if len(content) > 2000:
                content = content[:2000] + "...\n[Content truncated for length]"
            
            result_parts.append(content)
            result_parts.append(f"\n{'='*50}\n")
        
        result = "\n".join(result_parts)
        
        logging.info(f"TOOL: pdf_extract | OUTPUT: Extracted {len(docs)} pages from PDF")
        return result
        
    except Exception as e:
        error_msg = f"Error extracting PDF: {str(e)}"
        logging.error(f"TOOL: pdf_extract | ERROR: {error_msg}")
        return error_msg


@tool
def generate_code(task_description: str) -> str:
    """
    Generate Python code using Cerebras AI for a given programming task.
    
    Use this tool when user asks to "write code", "create a function", "implement algorithm", 
    or any request to generate/create code. Does NOT execute the code.
    
    Args:
        task_description: Description of what the code should do (e.g., "sort a list", "calculate fibonacci")
    
    Returns:
        str: Generated Python code ready to use
    """
    logging.info(f"TOOL: generate_code | INPUT: {task_description}")
    
    try:
        # Import Cerebras (only when needed)
        from cerebras.cloud.sdk import Cerebras
        
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            result = "Error: CEREBRAS_API_KEY environment variable is not set"
            logging.info(f"TOOL: generate_code | OUTPUT: {result}")
            return result
        
        # Create Cerebras client
        client = Cerebras(api_key=api_key)
        
        # System prompt for code generation
        system_prompt = """You are an expert Python programmer. Generate clean, efficient, and well-commented Python code based on the user's request. 

Rules:
- Only return the Python code, no explanations or markdown
- Include helpful comments in the code
- Make the code production-ready and follow best practices
- If the task is complex, break it into functions
- Include example usage if appropriate"""
        
        # Generate code using Cerebras
        response = client.chat.completions.create(
            model="llama-3.3-70b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_description}
            ]
        )
        
        # Extract the generated code
        generated_code = response.choices[0].message.content
        
        # Clean up the code (remove markdown if present)
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0].strip()
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].split("```")[0].strip()
        
        result = f"Generated Python code for: {task_description}\n\n{generated_code}"
        
        logging.info(f"TOOL: generate_code | OUTPUT: Generated {len(generated_code)} characters of code")
        return result
        
    except Exception as e:
        result = f"Error generating code: {str(e)}"
        logging.info(f"TOOL: generate_code | OUTPUT: {result}")
        return result


@tool
def execute_code(python_code: str) -> str:
    """
    Execute Python code in a secure E2B sandbox environment and return the output.
    
    Use this tool when user asks "what's the output", "run this code", "execute this", 
    or wants to see the result of code execution. Runs code safely in isolation.
    
    Args:
        python_code: Python code to execute (can be multi-line)
    
    Returns:
        str: Execution output including stdout, stderr, and any results
    """
    logging.info(f"TOOL: execute_code | INPUT: {python_code[:100]}...")
    
    try:
        # Import E2B (only when needed)
        from e2b_code_interpreter import Sandbox
        
        api_key = os.getenv("E2B_API_KEY")
        if not api_key:
            result = "Error: E2B_API_KEY environment variable is not set"
            logging.info(f"TOOL: execute_code | OUTPUT: {result}")
            return result
        
        # Clean up the code (remove markdown if present)
        clean_code = python_code
        if "```python" in clean_code:
            clean_code = clean_code.split("```python")[1].split("```")[0].strip()
        elif "```" in clean_code:
            clean_code = clean_code.split("```")[1].split("```")[0].strip()
        
        # Execute code in E2B Sandbox
        with Sandbox.create() as sandbox:
            execution = sandbox.run_code(clean_code)
            
            # Collect all output
            output_parts = []
            
            # Add stdout
            if execution.logs.stdout:
                stdout = ''.join(execution.logs.stdout).strip()
                if stdout:
                    output_parts.append(f"Output:\n{stdout}")
            
            # Add stderr (errors)
            if execution.logs.stderr:
                stderr = ''.join(execution.logs.stderr).strip()
                if stderr:
                    output_parts.append(f"Errors:\n{stderr}")
            
            # Add execution result if available
            if hasattr(execution, 'results') and execution.results:
                for result in execution.results:
                    if hasattr(result, 'text') and result.text:
                        output_parts.append(f"Result: {result.text}")
            
            # Format final result
            if output_parts:
                result = f"Code execution completed:\n\n" + "\n\n".join(output_parts)
            else:
                result = "Code executed successfully (no output produced)"
            
            logging.info(f"TOOL: execute_code | OUTPUT: Execution completed, {len(result)} chars output")
            return result
            
    except Exception as e:
        result = f"Error executing code: {str(e)}"
        logging.info(f"TOOL: execute_code | OUTPUT: {result}")
        return result


# # Add imports at the top
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
import tempfile
import os
import requests

@tool
def analyze_source_code(github_url: str) -> str:
    """
    Analyze source code from a GitHub repository or file URL.
    
    Parses code files (Python, JavaScript, Java, C++, etc.) and extracts functions,
    classes, and structure for analysis. Useful for understanding research implementations.
    
    Args:
        github_url: URL to GitHub file (e.g., https://github.com/user/repo/blob/main/file.py)
                   or raw GitHub URL (https://raw.githubusercontent.com/...)
    
    Returns:
        str: Parsed code structure with functions and classes separated
    """
    logging.info(f"TOOL: analyze_source_code | INPUT: {github_url}")
    
    try:
        # Convert GitHub URL to raw URL if needed
        if "github.com" in github_url and "/blob/" in github_url:
            raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        else:
            raw_url = github_url
        
        # Download the file
        response = requests.get(raw_url, timeout=10)
        if response.status_code != 200:
            return f"Could not download file from {github_url}. Status code: {response.status_code}"
        
        # Determine file extension and language
        file_ext = raw_url.split('.')[-1]
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{file_ext}', delete=False) as tmp_file:
            tmp_file.write(response.text)
            tmp_path = tmp_file.name
        
        try:
            # Load and parse the code
            loader = GenericLoader.from_filesystem(
                os.path.dirname(tmp_path),
                glob=os.path.basename(tmp_path),
                parser=LanguageParser(parser_threshold=50)  # Parse files >50 lines
            )
            
            docs = loader.load()
            
            if not docs:
                return f"Could not parse code from {github_url}"
            
            # Format results
            result_parts = [
                "=== Source Code Analysis ===",
                f"Source: {github_url}",
                f"Language: {docs[0].metadata.get('language', 'Unknown')}",
                f"Components found: {len(docs)}",
                f"\n{'='*50}\n"
            ]
            
            for i, doc in enumerate(docs, 1):
                content_type = doc.metadata.get('content_type', 'unknown')
                result_parts.append(f"\n--- Component {i}: {content_type} ---\n")
                
                # Limit content length
                content = doc.page_content
                if len(content) > 1500:
                    content = content[:1500] + "\n...[truncated]"
                
                result_parts.append(content)
                result_parts.append(f"\n{'='*50}\n")
            
            result = "\n".join(result_parts)
            
            logging.info(f"TOOL: analyze_source_code | OUTPUT: Parsed {len(docs)} code components")
            return result
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except Exception as e:
        error_msg = f"Error analyzing source code: {str(e)}"
        logging.error(f"TOOL: analyze_source_code | ERROR: {error_msg}")
        return error_msg



@tool
def duckduckgo_search(query: str) -> str:
    """
    Free web search using DuckDuckGo (no API key required).
    
    Use as backup when Tavily limit is reached or for additional web searches.
    Returns URL, title, and snippet from search results.
    
    Args:
        query: Search query string
    
    Returns:
        str: Search results with URLs, titles, and snippets
    """
    logging.info(f"TOOL: duckduckgo_search | INPUT: {query}")
    
    try:
        # Initialize DuckDuckGo with custom settings
        wrapper = DuckDuckGoSearchAPIWrapper(
            max_results=5,  # Return top 5 results
            region="wt-wt",  # Worldwide (use "us-en" for US, "in-en" for India)
            safesearch="moderate",  # moderate, strict, or off
            time="y"  # y=past year, m=past month, w=past week, d=past day
        )
        
        search = DuckDuckGoSearchResults(
            api_wrapper=wrapper,
            output_format="list"  # Return as list for better formatting
        )
        
        # Execute search
        results = search.invoke(query)
        
        if not results:
            return "No results found"
        
        # Format results
        result_parts = [
            f"=== DuckDuckGo Search Results ===",
            f"Query: {query}",
            f"Found: {len(results)} results\n"
        ]
        
        for i, result in enumerate(results, 1):
            result_parts.append(f"\n--- Result {i} ---")
            result_parts.append(f"Title: {result.get('title', 'N/A')}")
            result_parts.append(f"URL: {result.get('link', 'N/A')}")
            result_parts.append(f"Snippet: {result.get('snippet', 'N/A')}")
            result_parts.append("-" * 50)
        
        final_result = "\n".join(result_parts)
        
        logging.info(f"TOOL: duckduckgo_search | OUTPUT: {len(results)} results")
        return final_result
        
    except Exception as e:
        error_msg = f"DuckDuckGo search failed: {str(e)}"
        logging.error(f"TOOL: duckduckgo_search | ERROR: {error_msg}")
        return error_msg


# @tool
# def pdf_vision_extract(file_path: str) -> str:
#     """
#     Extract content from complex PDFs using AI vision (Gemini).
    
#     Best for PDFs with images, charts, tables, scanned documents, or complex layouts.
#     Uses Google Gemini vision to understand visual content that text-based extractors miss.
    
#     Use this when:
#     - PDF has images, charts, or diagrams you need to understand
#     - PDF is scanned or has poor text extraction
#     - PDF has complex tables or mixed layouts
#     - Regular pdf_extract doesn't work well
    
#     Args:
#         file_path: Path to PDF file (local path or URL)
    
#     Returns:
#         str: Extracted content in markdown format with visual understanding
#     """
#     logging.info(f"TOOL: pdf_vision_extract | INPUT: {file_path}")
    
#     try:
#         import nest_asyncio
#         from langchain_community.document_loaders.pdf import ZeroxPDFLoader
        
#         # Apply nest_asyncio for async support
#         nest_asyncio.apply()
        
#         # Get Google API key
#         api_key = os.getenv("GOOGLE_API_KEY")
#         if not api_key:
#             return "Error: GOOGLE_API_KEY not found in environment variables"
        
#         # Set environment variable for Gemini (Zerox uses GEMINI_API_KEY)
#         os.environ["GEMINI_API_KEY"] = api_key
        
#         # Initialize ZeroxPDFLoader with Gemini model
#         loader = ZeroxPDFLoader(
#             file_path=file_path,
#             model="gemini/gemini-1.5-flash"  # Using Gemini Flash
#         )
        
#         # Load documents (each page becomes a document)
#         docs = loader.load()
        
#         if not docs:
#             return f"Could not extract content from PDF: {file_path}"
        
#         # Format results
#         result_parts = [
#             "=== PDF Vision Extraction (AI) ===",
#             f"File: {file_path}",
#             f"Total Pages: {len(docs)}",
#             f"Model: Gemini 1.5 Flash (Vision)",
#             f"\n{'='*50}\n"
#         ]
        
#         # Add content from each page
#         for doc in docs:
#             page_num = doc.metadata.get('page', 'Unknown')
#             result_parts.append(f"\n--- Page {page_num} ---\n")
            
#             # Limit content per page to avoid token limits
#             content = doc.page_content
#             if len(content) > 2500:
#                 content = content[:2500] + "...\n[Content truncated for length]"
            
#             result_parts.append(content)
#             result_parts.append(f"\n{'='*50}\n")
        
#         result = "\n".join(result_parts)
        
#         logging.info(f"TOOL: pdf_vision_extract | OUTPUT: Extracted {len(docs)} pages using Gemini vision")
#         return result
        
#     except Exception as e:
#         error_msg = f"Error extracting PDF with vision: {str(e)}"
#         logging.error(f"TOOL: pdf_vision_extract | ERROR: {error_msg}")
#         return error_msg


# List of all available tools
def get_tools():
    """Return list of all available tools for the agent"""
    return [
        tavily_search, 
        fetch_url_content, 
        wikipedia_search, 
        arxiv_search, 
        youtube_transcript, 
        pubmed_search, 
        pdf_extract,
        duckduckgo_search,
        analyze_source_code,
        generate_code,
        execute_code
    ]
