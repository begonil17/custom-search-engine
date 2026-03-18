from read_documents import load_tfidf, load_invertedindex, read_pdf_files
from text_preprocessing import preprocess_text

files_path = r'.\documents'

tf_idf_scores = load_tfidf()
inverted_index = load_invertedindex()
documents = read_pdf_files(files_path)

if inverted_index is None or tf_idf_scores is None:
    print("Error: Could not load search index. Make sure there are PDF files in the documents folder.")
    exit(1)

def search(query, documents, inverted_index, tf_idf_scores, top_n):
    scores = []
    # Preprocess the query
    query_terms = preprocess_text(query)
    if not query_terms:
        print("Query not read")
        return None
    
    relevant_docs = set()
    for term in query_terms:
        if term in inverted_index:
            for d in inverted_index[term]:
                relevant_docs.add(d) 
    relevant_docs = list(relevant_docs)

    for doc in relevant_docs:
        score = 0.0
        for term in query_terms:
            if term in tf_idf_scores.get(doc, {}):
                score += tf_idf_scores[doc][term]
        #Normalize score
        score /= len(query_terms)
        scores.append((doc, score))

    # Sort by score
    scores.sort(key=lambda x: x[1], reverse=True)
    # Return top N results
    results = []
    for doc, score in scores[:top_n]:
        if score > 0:
            results.append({
                'document': doc,
                'relevance score': score,
                'document content': documents[doc] 
            })
    return results

print("="*60)
print("A TF-IDF based search engine to search for relevant documents.\n(type 'quit' to exit)")
print("="*60)

while True:
    print("\n<< What are you looking for? ฅ^•ﻌ•^ฅ")
    search_query = input(">>")

    if search_query.strip().lower() in ('quit', 'exit', 'q'):
        print("Goodbye!")
        break

    if not search_query.strip():
        print("Please enter a search query.")
        continue

    results = search(search_query, documents, inverted_index, tf_idf_scores, 3)

    if not results:
        print("No relevant documents found.")
    else:
        for i, result in enumerate(results, 1):
            print(f"\n{'─'*60}")
            print(f"Result {i}: {result['document']}")
            print(f"Relevance score: {result['relevance score']:.4f}")
            print(f"Document Content: {result['document content']}")