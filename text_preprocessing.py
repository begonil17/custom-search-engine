import string

# Load stop words from file for text preprocessing
with open('StopWords.txt', 'r') as f:
    exec(f.read())  # loads STOP_WORDS as a set

def stem_token(token):
    """Simple stemming function (more complex algorithms can be used in practical applications)"""
    # Handle common suffixes
    suffixes = ['ing', 'ly', 'ed', 'es', 's']
    for suffix in suffixes:
        if token.endswith(suffix) and len(token) > len(suffix):
            return token[:-len(suffix)]
    return token

def preprocess_text(text):
    """Preprocessing: lowercasing, removing punctuation, tokenization, stop word removal, and stemming."""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    # Tokenization (simple space splitting; more complex logic can be used in practical applications)
    tokens = text.split()
    # Remove stop words and empty strings
    tokens = [token for token in tokens if token not in STOP_WORDS and token.strip() != '']
    # Simple stemming (simplified version)
    tokens = [stem_token(token) for token in tokens]
    return tokens
