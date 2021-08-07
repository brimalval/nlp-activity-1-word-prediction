from flask import Flask, render_template, request
from nltk.probability import FreqDist
from nltk.corpus import abc
from nltk.util import bigrams, trigrams
import re

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/generate', methods=["POST", "GET"])
def generate():
	words = request.form['sentence'].strip().split(' ')
	puncs = re.compile(r'[-,.:;?!\'"()|0-9]')
	rr_tokens = abc.words('rural.txt')
	post_punc = []
	for token in rr_tokens:
		new_token = puncs.sub("", token)
		if len(new_token) > 0:
			post_punc.append(token)
	word_counts = FreqDist()
	# Used to figure out if the search should be broadened
	# If the top result has less than this freq, broaden
	FREQ_THRESHHOLD = 10
	SUGGESTIONS_THRESHHOLD = 5
	insufficient_results = True
	if len(words) > 2:
		rr_trigrams = list(trigrams(post_punc))
		for trigram in rr_trigrams:
			if trigram[0].lower() == words[-3].lower() and trigram[1].lower() == words[-2].lower() and trigram[2][:len(words[-1])].lower() == words[-1]:
				word_counts[trigram[2].lower()] += 1
		most_common = word_counts.most_common(50);
		suggestions = len(most_common);
		insufficient_results = suggestions == 0 or (suggestions <= SUGGESTIONS_THRESHHOLD and most_common[0][1] <= FREQ_THRESHHOLD)
	if insufficient_results and len(words) == 2:
		rr_bigrams = list(bigrams(post_punc))
		for bigram in rr_bigrams:
			if bigram[0].lower() == words[-2].lower() and bigram[1].lower()[:len(words[-1])] == words[-1].lower():
				word_counts[bigram[1].lower()] += 1
		most_common = word_counts.most_common(50);
		suggestions = len(most_common);
		insufficient_results = suggestions == 0 or (suggestions <= SUGGESTIONS_THRESHHOLD and most_common[0][1] <= FREQ_THRESHHOLD)
	if insufficient_results:
		for word in post_punc:
			if word[:len(words[-1])].lower() == words[-1].lower():
				word_counts[word.lower()] += 1
 
	return render_template('index.html', 
	sentence=request.form['sentence'],
	word_counts=word_counts.most_common(50))

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)