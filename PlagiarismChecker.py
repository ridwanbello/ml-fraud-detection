
#Import all nltk methods
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from os.path import dirname, join
import requests, time

# Import numpy for calculating distance
import numpy as np
import rabin_karp

class PlagiarismChecker:
    def __init__(self, file_a, file_b):
        self.file_a = file_a
        self.file_b = file_b
        self.hash_table = {"a": [], "b": []}
        self.k_gram = 4
        #content_a =self.file_a
        #content_b = self.file_b
        try:
            content_a = self.clean_content(self.file_a)
            #content_b = self.get_url_content(self.file_b)
            content_b = self.clean_content(self.file_b)
            self.calculate_hash(content_a, "a")
            self.calculate_hash(content_b, "b")
        except:
            print("Exception")  

    # calaculate hash value of the file content
    # and add it to the document type hash table
    def calculate_hash(self, content, doc_type):
        text = self.prepare_content(content)
        text = "".join(text)
        print(text)

        text = rabin_karp.rolling_hash(text, self.k_gram)
        for _ in range(len(content) - self.k_gram + 1):
            self.hash_table[doc_type].append(text.hash)
            if text.next_window() == False:
                break

    def get_rate(self):
        return self.calaculate_plagiarism_rate(self.hash_table)

    # calculate the plagiarism rate using the plagiarism rate formula
    def calaculate_plagiarism_rate(self, hash_table):
        th_a = len(hash_table["a"])
        th_b = len(hash_table["b"])
        a = hash_table["a"]
        b = hash_table["b"]
        sh = len(np.intersect1d(a, b))
        # print(sh, a, b)
        # print(sh, th_a, th_b)

        # Formular for plagiarism rate
        # P = (2 * SH / THA * THB ) 100%
        p = (float(2 * sh)/(th_a + th_b)) * 100
        return p

    # get content from file
    def get_file_content(self, filename):
        file = open(filename, 'r+', encoding="utf-8")
        data = file.read()
        return data

    # Get content from url
    def get_url_content(self, filename):
        lines = ""
        response = requests.get(filename)
        response.encoding = "utf-8"
        data = response.text
        for line in data.split('\r\n'):
            lines += " "+line
        return lines

    # Get content from url
    def get_url_content_only(self, filename):
        response = requests.get(filename)
        response.encoding = "utf-8"
        data = response.text
        return data

    # Clean content
    def clean_content(self, data):
        try:
            lines = data.replace('\n',' ').replace('\r', ' ').replace('\'', ' ')
            return lines
        except:
            print("Error cleaning content there")


    # Prepare content by removing stopwords, steemming and tokenizing
    def prepare_content(self, content):
        # STOP WORDS
        stop_words = set(stopwords.words('english'))
        # TOKENIZE
        word_tokens = word_tokenize(content)
        filtered_content = []
        # STEMMING
        porter = PorterStemmer()
        for w in word_tokens:
            if w not in stop_words:
                w = w.lower()
                word = porter.stem(w)
                filtered_content.append(word)

        return filtered_content