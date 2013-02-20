#!/usr/bin/python
# vim: set fileencoding=utf-8

import json
import codecs
from termcolor import colored
import re

file = '../data/questions.json'
importance = [ 'Irrelevant',
	colored('A little important', 'green'),
	colored('Somewhat important', 'green', attrs=['underline']),
	colored('Very important', 'red', 'on_yellow'),
	colored('Mandatory', 'red', 'on_grey'),
]

# json_data=open('test.json')
json_data = codecs.open(file, 'r', 'utf-8')
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
		if pub: visability = "publicly"
		else:	visability = "privately"

		print("%s (%d: %s, %s answered):" % (text, imp, importance[imp], visability))
		for ans_id in sorted(que['data'][que_id]['answers']):
			ans_text = que['data'][que_id]['answers'][ans_id]['text']
			my_ans = que['data'][que_id]['answers'][ans_id]['isMine']
			match_ans = que['data'][que_id]['answers'][ans_id]['isMatch']
			color_attrs = []
			if my_ans:
				color_attrs.append('underline')
			if match_ans:
				print(colored('\t%s' % (ans_text), 'green', attrs=color_attrs))
			else:
				print(colored('\t%s' % (ans_text), attrs=color_attrs))
			if my_ans and exp:
				print(" (%s)" % (exp))

useranswer = raw_input("Do you want to search for a question (if no you will see all questions …)? ")
if re.match(r"(y|j)", useranswer, re.I):
	qQue = {}
	for que_id in que['data']:
		text = que['data'][que_id]['text']
		qQue[text] = que_id
	
	print('You can use a python regular expression to match against the questions.')
	print('If you are done you can enter a empty pattern to exit the program.')
	while True:
		pattern = raw_input('Please enter a pattern: ')
		if re.match(r"\s*\Z", pattern): break

		try:
			matches = [text for text in qQue if re.search(pattern, text, re.I)]
		except:
			print('Your regular expresion failed', detail)
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
else:
	for id in sorted([int(id) for id in que['data']]):
		printIt(str(id), None)
