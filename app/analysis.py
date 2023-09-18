import json
import re
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from gensim.models import CoherenceModel
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
import pyLDAvis.gensim_models
from gensim.models import Phrases
from bertopic import BERTopic
from pyLDAvis import prepare
import gensim

# Set up the lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Define the path
DATA_PATH = "/home/erniesg/code/erniesg/berlayar/raw_data/weibo/weibo_en.jsonl"

def preprocess_content(content):
    # Tokenize
    tokens = re.findall(r'\w+', content.lower())

    # Remove specific words
    remove_words = ["http", "also"]
    tokens = [token for token in tokens if token not in remove_words]

    # Lemmatize and remove stopwords
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]

    return ' '.join(tokens)

def load_and_preprocess_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    # Preprocess the 'content' field for each entry
    for entry in data:
        entry['content_cleaned'] = preprocess_content(entry['content'])

    return data
def print_lda_topics(model, vectorizer, n_words=10):
    """
    Print the top n_words for each topic from the LDA model.

    Parameters:
    - model : The LDA model.
    - vectorizer : The vectorizer used to transform the texts.
    - n_words : The number of top words to print for each topic.
    """
    words = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(model.components_):
        print(f"\nTopic #{topic_idx + 1}:")
        print(" ".join([words[i] for i in topic.argsort()[:-n_words - 1:-1]]))

# Load and preprocess data
data = load_and_preprocess_data(DATA_PATH)
print("Data loaded and preprocessed.")

# Print a snippet of the data for visualization
print("\nSample data (Before and After Preprocessing):\n")
for i, entry in enumerate(data[:5]):
    print(f"Sample {i+1} Original Content: {entry['content']}")
    print(f"Sample {i+1} Cleaned Content: {entry['content_cleaned']}\n")

# Extract cleaned content from the data
cleaned_content = [entry['content_cleaned'] for entry in data]
# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
tfidf = vectorizer.fit_transform(cleaned_content)

def print_lda_topics(lda, vectorizer):
    terms = vectorizer.get_feature_names_out()
    for idx, topic in enumerate(lda.components_):
        print(f"Topic #{idx + 1}:")
        print(" ".join([terms[i] for i in topic.argsort()[:-10 - 1:-1]]))
        print()

# Assuming cleaned_content is a list of preprocessed documents
texts = [doc.split() for doc in cleaned_content]

# Create a dictionary representation of the documents
dictionary = Dictionary(texts)

# Convert dictionary into a bag-of-words corpus
corpus = [dictionary.doc2bow(text) for text in texts]

coherence_values = []
model_list = []
topic_range = range(2, 20)  # example range, adjust as necessary

for num_topics in topic_range:
    # Train LDA
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda_output = lda.fit_transform(tfidf)

    # Compute Coherence Score using gensim's c_v measure
    lda_model_gensim = gensim.models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, random_state=42)
    coherencemodel = CoherenceModel(model=lda_model_gensim, texts=texts, dictionary=dictionary, coherence='c_v')
    coherence_values.append(coherencemodel.get_coherence())

# Print coherence scores
for num_topics, coherence in zip(topic_range, coherence_values):
    print(f"Number of Topics: {num_topics}, Coherence Score: {coherence:.4f}")

# Identify the number of topics with the highest coherence score
optimal_num_topics = topic_range[coherence_values.index(max(coherence_values))]
print(f"\nThe optimal number of topics is: {optimal_num_topics}")

# Train LDA using the optimal number of topics and print out the topics
lda_optimal = LatentDirichletAllocation(n_components=optimal_num_topics, random_state=42)
lda_output_optimal = lda_optimal.fit_transform(tfidf)
print("\nTopics from the LDA model with optimal number of topics:\n")
print_lda_topics(lda_optimal, vectorizer)

# Use BERTopic with enhanced parameters:
topic_model = BERTopic(language="english", n_gram_range=(1, 3), calculate_probabilities=True, min_topic_size=10)
topics, probs = topic_model.fit_transform(cleaned_content)
print("\nTopics from BERT model:\n")

# Print out the most frequent topics
topic_freq = topic_model.get_topic_freq()
print(topic_freq.head(10))

# To see the topics and associated words:
for topic in topic_freq['Topic'][:10]:
    words = topic_model.get_topic(topic)
    print(f"Topic {topic}: {words}\n")

# Reduce topics without setting a fixed number
# new_topics, new_probs = topic_model.reduce_topics(cleaned_content, topics, probs)

# Use BERTopic with Sentence-BERT embeddings
sbert_topic_model = BERTopic(embedding_model="paraphrase-MiniLM-L6-v2", language="english", calculate_probabilities=True)
sbert_topics, sbert_probs = sbert_topic_model.fit_transform(cleaned_content)

# Print out the most frequent topics for the Sentence-BERT model
sbert_topic_freq = sbert_topic_model.get_topic_freq()
print("\nTopics using Sentence-BERT embeddings:\n")
print(sbert_topic_freq.head(15))

# To see the topics and associated words from Sentence-BERT model:
for topic in sbert_topic_freq['Topic'][:15]:
    words = sbert_topic_model.get_topic(topic)
    print(f"Topic {topic}: {words}\n")
