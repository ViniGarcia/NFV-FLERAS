from sklearn.feature_extraction.text import TfidfVectorizer

tests = [["MehOriginal.py", "MehIndex.py", "MehMulti.py"], ["MehOriginalH.py", "MehIndexH.py", "MehMultiH.py"], ["MijOriginal.py", "MijIndex.py", "MijMulti.py"]]

for text_files in tests:
    documents = [open(f).read() for f in text_files]
    tfidf = TfidfVectorizer().fit_transform(documents)
    pairwise_similarity = tfidf * tfidf.T
    print(text_files)
    print(pairwise_similarity[0])
    print()
