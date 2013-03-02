#!/usr/bin/python
# vim: set fileencoding=utf-8

import sys
import signal
import json
import codecs
from termcolor import colored
import re

show_allowed_answer = 1
show_importance = 1
file = '../data/questions.json'
if len(sys.argv) > 1:
	file = sys.argv[1]

def signal_handler(signal, frame):
    print('\nExiting. Have a nice day …')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

importance = [ 'Irrelevant',
	colored('A little important', 'green'),
	colored('Somewhat important', 'green', attrs=['underline']),
	colored('Very important', 'red', 'on_yellow'),
	colored('Mandatory', 'red', 'on_grey'),
]

# json_data=open('test.json')
try:	json_data = codecs.open(file, 'r', 'utf-8')
except IOError as detail:
	print('File '+ file +' is not readable: '+ detail[1])
	print('Please give me a JSON file as parameter …')
	sys.exit(1)
que = json.load(json_data)
json_data.close()
date = que['date']
print('The data is from %s\n' % (date))

def printIt(que_id, pattern):
	text = que['data'][que_id]['text']
	if pattern:
		try:
			res = re.search('(?P<pre>.*?)(?P<match>'+pattern+')(?P<post>.*)', text)
			text = res.group('pre') + colored(res.group('match'), 'blue') + res.group('post')
		except:	pass## This will happen if the pattern matches at ^ and pre would be empty
			## and the regular expression would fail … ??
	if que['data'][que_id]['isSkipped']:
		print(que_id, "is skipped:", text)
	else:
		imp = que['data'][que_id]['importance']
		exp = que['data'][que_id]['explanation']
		pub = que['data'][que_id]['isPublic']
		visability = 'publicly' if pub else 'privately'
		imp_text = '%d: %s, ' % (imp, importance[imp]) if show_importance else ''

		print("%s (%s%s answered):" % (text, imp_text, visability))
		for ans_id in sorted(que['data'][que_id]['answers']):
			ans_text = que['data'][que_id]['answers'][ans_id]['text']
			my_ans = que['data'][que_id]['answers'][ans_id]['isMine']
			match_ans = que['data'][que_id]['answers'][ans_id]['isMatch']
			color_attrs = []
			if my_ans:
				color_attrs.append('underline')
			if match_ans and show_allowed_answer:
				sys.stdout.write(colored('\t%s' % (ans_text), 'green', attrs=color_attrs))
			else:
				sys.stdout.write(colored('\t%s' % (ans_text), attrs=color_attrs))
			if my_ans and exp:
				sys.stdout.write(" (%s)" % (exp))
			print('')
	print('')


qQue = {}
for que_id in que['data']:
	text = que['data'][que_id]['text']
	qQue[text] = que_id

print('You can use a python regular expression to match against the questions.')
print('The regular expression is case insensitive.')
print('If you are done you can enter a empty pattern to exit the program.')
while True:
	pattern = raw_input('Please enter a pattern: ')
	if re.match(r"\s*\Z", pattern):
		print('Have fun')
		break

	try:
		matches = [text for text in qQue if re.search(pattern, text, re.I)]
	except:
		print('Your regular expresion failed')
		continue
	que_id_l = [ qQue[text] for text in matches]
	word_times = 'time'
	match_count = len(que_id_l)
	if match_count == 1: word_times += 's'
	print('Matched %d %s:' % (match_count, word_times))
	if match_count > 20:
		if not re.match(r"(y|j)", raw_input("Do you really want to print all questions? "), re.I):
			continue
	que_id_l.sort(key=int)
	for que_id in que_id_l:
		printIt(que_id, pattern)
