# Custom Search Engine

This project is a custom-built search engine that retrieves the most relevant documents based on a query, using an inverted index and TF-IDF scoring.

## Features

- **Inverted Index + TF-IDF**
  - Efficient term-based lookup using an inverted index
  - TF-IDF scoring implemented manually (no external libraries)

- **Persistent Storage (SQL Database)**
  - Stores inverted index and TF-IDF scores in a database
  - Avoids recomputation unless necessary

- **Update Detection**
  - Tracks file modification timestamps
  - Detects:
    - Modified documents
    - Newly added documents
    - Deleted documents
  - Rebuilds index only when changes are detected

- **Efficient Query Processing**
  - Returns **top 3 most relevant documents**
  - Outputs:
    - Document name
    - Relevance score
    - Document content

## How It Works

1. Documents from a specified directory are read and tokenized
2. An inverted index is constructed
3. TF-IDF scores are computed manually
4. Index and scores are stored in a SQL database
5. On subsequent runs:
   - File timestamps are compared
   - Index is recomputed only if changes are detected
6. Queries are processed and ranked using TF-IDF scores

## Installation & Usage

### Prerequisites
- Python 3.10+

### Installation
1. Clone the repository:
```bash
git clone https://github.com/begonil17/custom-search-engine
cd custom-search-engine
```
2. Install required packages
```bash
pip install -r requirements.txt
```
4. Add your documents
- Place your documents inside the documents/ folder
- Documents must be in .pdf format
- The repository already includes 10 sample PDF documents for testing

3. Run the application
```bash
python main.py
```
4. Enter your query
- Type your search query in the terminal
- The system will return the top 3 most relevant documents along with:
    - Document name
    - Relevance score
    - Document content

## Future Improvements

- Add a simple frontend interface (HTML/CSS)
- Return most relevant **text chunks** instead of full documents
- Integrate an LLM for:
  - Summarization
  - Better query understanding
  - Interactive search experience

## References
This project was developed independently by adapting and expanding the ideas presented in the tutorial:

- [How to Build a Search Engine from Scratch in Python (No External Packages)](https://leapcell.medium.com/how-to-build-a-search-engine-from-scratch-in-python-no-external-packages-36cc9e0ba9d0)