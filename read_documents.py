import os
import glob
from pypdf import PdfReader
import sqlite3
import math
from text_preprocessing import preprocess_text

files_path = r'.\documents'
DB_PATH = 'InvertedIndex.db'

# Read and return the text content of each document
def read_pdf_files(file_path):
    pdf_files = sorted(glob.glob(os.path.join(file_path, '*.pdf')))
    doc_texts = {}

    for filename in pdf_files:
        print(f"Processing file: {filename}")
        reader = PdfReader(filename)
        totalText = ""
        for page in reader.pages:
            totalText += page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False)
        doc_texts[filename] = totalText

    return doc_texts

# Preprocess the text of each document
def process_texts(doc_texts):
    doc_tokens = {}

    for doc in doc_texts:
        doc_tokens[doc] = preprocess_text(doc_texts[doc])

    return doc_tokens

def build_inverted_index(doc_tokens):
    """Read PDFs, build inverted index and per-document token lists."""
    inverted_index = {}

    for doc in doc_tokens:
        for term in doc_tokens[doc]:
            if term in inverted_index:
                if doc not in inverted_index[term]:
                    inverted_index[term].append(doc)
            else:
                inverted_index[term] = [doc]

    return inverted_index

def calculate_tfidf(doc_tokens, inverted_index):
    """Calculate TF-IDF for every (doc, term) pair. Returns {doc_id: {term: tfidf_score, ...}, ...}"""
    tf_idf_scores = {}
    num_docs = len(doc_tokens)

    # Calculate document frequency for all terms
    doc_freq = {term: len(docs) for term, docs in inverted_index.items()}

    for doc_name, tokens in doc_tokens.items():
        num_terms = len(tokens)
        doc_tf_idf = {}
        for term in tokens:
            if term not in doc_tf_idf:  # Only calculate once per term per document
                tf = tokens.count(term) / num_terms
                idf = math.log10(num_docs / doc_freq[term])
                doc_tf_idf[term] = tf * idf
        tf_idf_scores[doc_name] = doc_tf_idf

    return tf_idf_scores

def save_to_db(inverted_index, tf_idf_scores):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS InvInd (
            term TEXT PRIMARY KEY,
            documents TEXT
        )
    ''')

    # Separate table for tf-idf so scores are stored per (document, term) pair
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TfIdf (
            doc_name TEXT,
            term TEXT,
            tfidf REAL,
            PRIMARY KEY (doc_name, term)
        )
    ''')

    # Stores last-modified timestamp per document to detect file changes cheaply
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DocMeta (
            doc_name TEXT PRIMARY KEY,
            mtime REAL
        )
    ''')

    # Clear stale data so removed/renamed documents don't linger
    cursor.execute('DELETE FROM InvInd')
    cursor.execute('DELETE FROM TfIdf')
    cursor.execute('DELETE FROM DocMeta')

    for term, documents in inverted_index.items():
        cursor.execute(
            'INSERT INTO InvInd (term, documents) VALUES (?, ?)',
            (term, ', '.join(documents))
        )

    for doc_name, term_scores in tf_idf_scores.items():
        for term, score in term_scores.items():
            cursor.execute(
                'INSERT INTO TfIdf (doc_name, term, tfidf) VALUES (?, ?, ?)',
                (doc_name, term, score)
            )
        cursor.execute(
            'INSERT INTO DocMeta (doc_name, mtime) VALUES (?, ?)',
            (doc_name, os.path.getmtime(doc_name))
        )

    conn.commit()
    conn.close()
    print("Inverted index and TF-IDF scores saved to InvertedIndex.db")

def load_invertedindex():
    """Load inverted index from DB when the document set and all modification times match. Reread the files otherwise"""
    current_files = set(sorted(glob.glob(os.path.join(files_path, '*.pdf'))))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # If DocMeta table doesn't exist the DB was never populated
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DocMeta'")
    if not cursor.fetchone():
        conn.close()
        return None

    stored = {row[0]: row[1] for row in cursor.execute('SELECT doc_name, mtime FROM DocMeta')}

    # Trigger recompute if files were added or removed
    if set(stored.keys()) != current_files:
        conn.close()
        print("Files were added/removed. Recomputing inverted index and TF-IDF scores...")
        read_save()
        return load_invertedindex()

    # Trigger recompute if any file was modified since it was last indexed
    for doc_name in current_files:
        if os.path.getmtime(doc_name) != stored[doc_name]:
            conn.close()
            print("Files were modified. Recomputing inverted index and TF-IDF scores...")
            read_save()
            return load_invertedindex()

    inverted_index = {}
    for term, documents in cursor.execute('SELECT term, documents FROM InvInd'):
        inverted_index[term] = [d.strip() for d in documents.split(',')]

    conn.close()
    print("Loaded inverted index from InvertedIndex.db")
    return inverted_index

def load_tfidf():
    """Load TF-IDF scores from DB when the document set and all modification times match. Reread the files otherwise"""
    current_files = set(sorted(glob.glob(os.path.join(files_path, '*.pdf'))))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # If DocMeta table doesn't exist the DB was never populated
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DocMeta'")
    if not cursor.fetchone():
        conn.close()
        return None

    stored = {row[0]: row[1] for row in cursor.execute('SELECT doc_name, mtime FROM DocMeta')}

    # Trigger recompute if files were added or removed
    if set(stored.keys()) != current_files:
        conn.close()
        print("Files were added/removed. Recomputing inverted index and TF-IDF scores...")
        read_save()
        return load_tfidf()

    # Trigger recompute if any file was modified since it was last indexed
    for doc_name in current_files:
        if os.path.getmtime(doc_name) != stored[doc_name]:
            conn.close()
            print("Files were modified. Recomputing inverted index and TF-IDF scores...")
            read_save()
            return load_tfidf()

    tf_idf_scores = {}
    for doc_name, term, tfidf in cursor.execute('SELECT doc_name, term, tfidf FROM TfIdf'):
        tf_idf_scores.setdefault(doc_name, {})[term] = tfidf

    conn.close()
    print("Loaded TF-IDF scores from InvertedIndex.db")
    return tf_idf_scores

def read_save():
    doc_texts = read_pdf_files(files_path)
    doc_tokens = process_texts(doc_texts)
    inverted_index = build_inverted_index(doc_tokens)
    tf_idf_scores = calculate_tfidf(doc_tokens, inverted_index)
    save_to_db(inverted_index, tf_idf_scores)

# Main execution - Only recompute if the DB is missing or stale

if load_tfidf() is None:
    read_save()
