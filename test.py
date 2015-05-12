import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Value(ndb.Model):
	value = ndb.StringProperty(indexed=False)
	name = ndb.StringProperty(indexed=True)
	text = ndb.StringProperty(indexed=False)

class Question(ndb.Model):
	number = ndb.IntegerProperty()
	title = ndb.StringProperty(indexed=False)
	name = ndb.StringProperty(indexed=True)
	qtype = ndb.StringProperty(indexed=False)

class Result(ndb.Model):
	gender = ndb.StringProperty(indexed=True)
	results = ndb.JsonProperty(indexed=False, repeated = True)


class Survey(webapp2.RequestHandler):

    def get(self):

        value1 = Value(value = "married", text = "Married", name = "relationship")
        value2 = Value(value = "single", text = "Single", name = "relationship")
        value3 = Value(value = "divorced", text = "Divorced", name = "relationship")
        value4 = Value(value = "widowed", text = "Widowed", name = "relationship")
        value5 = Value(value = "separated", text = "Separated", name = "relationship")
        value6 = Value(value = "relationship", text = "Relationship", name = "relationship")

        value7 = Value(value= "italy", text = "Italy", name = "countries")
        value8 = Value(value = "canada", text = "Canada", name = "countries")

        value9 = Value(value= "male", text = "Male", name = "gender")
        value10 = Value(value = "female", text = "Female", name = "gender")

        question = Question(number = 1,
            title = "What is your gender?",
            name = "gender",
            qtype = "radio")

        question2 = Question(number = 2,
            title = "What is your relationship status?",
            name = "relationship",
            qtype = "radio")
        question3 = Question(number = 2,
            title = "Which countries have you visisted?",
            name = "countries",
            qtype = "checkbox")

        # question.put()
        # question2.put()
        # question3.put()
        # value1.put()
        # value2.put()
        # value3.put()
        # value4.put()
        # value5.put()
        # value6.put()
        # value7.put()
        # value8.put()
        # value9.put()
        # value10.put()

        questions = Question.query().fetch()

        values = Value.query().fetch()

        template_values = {
        	'questions': questions,
        	'values': values
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))



class AddSurvey(webapp2.RequestHandler):
    def post(self):
        

        questions = Question.query().fetch()
        results = []

        for question in questions:

        	if question.name == 'gender':
        		gender = self.request.get(question.name);
        	else:
        		if question.qtype == "checkbox":
				alist = self.request.get(question.name, allow_multiple=True)
				print alist
        			for a in alist:
        				r = {}
        				r[question.name] = a
        				results.append(r)
        		else:
        			r = {}
        			r[question.name] = self.request.get(question.name)
        			results.append(r)
        		print question
        		print results
        		# results[question.name] = self.request.get(question.name)

        result = Result(gender = gender, results = results)
        result.put()


        template = JINJA_ENVIRONMENT.get_template('addsurvey.html')
        self.response.write(template.render())

        self.redirect('/results')

class Results(webapp2.RequestHandler):
    def get(self):

    	results = Result.query().fetch()
        questions = Question.query().fetch()
        values = Value.query().fetch()

        query = Result.query()
        maleResultQuery = query.filter(ndb.GenericProperty("gender") == "male").fetch(10)
       	femaleResultQuery = Result.query(ndb.GenericProperty("gender") == "female").fetch()

        maleResults = {}
        femaleResults = {}

        for result in maleResultQuery:
        	for r in result.results:
	        	for k,v in r.items():
	        		q = Question.query(k == Question.name).fetch()
	        		answers = maleResults.get(k)

	        		if answers is None:
	        			answers = {}
	        		
	    			a = answers.get(v)
	    			if a is None:
	    				answers[v] = 1
	    				maleResults[k] = answers
	    			else:
	        			answers[v] = answers.get(v) + 1

        for result in femaleResultQuery:
        	for r in result.results:
	        	for k,v in r.items():
	        		q = Question.query(k == Question.name).fetch()
	        		answers = femaleResults.get(k)

	        		if answers is None:
	        			answers = {}
	        		
	    			a = answers.get(v)
	    			if a is None:
	    				answers[v] = 1
	    				femaleResults[k] = answers
	    			else:
	        			answers[v] = answers.get(v) + 1

        	
        
        

        template_values = {
        	'maleResults' : maleResults,
        	'femaleResults' : femaleResults,
            'results' : results,
            'questions' : questions,
            'values' : values
        }


        template = JINJA_ENVIRONMENT.get_template('results.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', Survey),
    ('/add', AddSurvey),
    ('/results', Results)
], debug=True)