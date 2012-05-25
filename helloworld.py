import cgi
import csv
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import google.appengine.ext.db


class Form(db.Expando):
	''''create entities for database'''
	name=db.StringProperty()
	namelist=db.StringListProperty()
	titles=db.StringListProperty()
	editors=db.StringListProperty()
	

class MainPage(webapp.RequestHandler):
	''''Home page handler'''
	def get(self):
		#check if valid google account
		user = users.get_current_user()
		
		if user: 								#if valid logged in user
		
			username = user.nickname()		 	#define name in loop
			SH_list = csv.reader(open('SH_list.csv'),delimiter =",")		#open csv file to be used
			theclass=""
			for row in SH_list:					
				if row[0]== username:
					theclass = row[2]			#define theclass and get the class
					break
			self.response.out.write('''<!DOCTYPE HTML>
	<html>
	<head>
	<meta charset="utf-8">
	<title>%s class list</title>
	</head>

	<body>
		<div align = "right" >
		<h4><a href = "%s" >LOGOUT</a></h4>
		</div>
		<div>
		<h2>Welcome to DHS LIST! <strong>%s</strong>!</h2>
		<h3> %s </h3>
		</div>'''%(theclass,users.create_logout_url(self.request.uri),username,theclass))
					
			# to get the whole database from gql so to be able to edit
			myform = Form.gql("WHERE name = '%s'"%(theclass)).get()		
			
			#if not in database
			if not myform:
				SH_list = csv.reader(open('SH_list.csv'),delimiter=",")
				classlist = []
				insert_form = Form()							#assign database class to a variable
				for row in SH_list:					# get all the people in the class to be in the class list
					if row[2] == theclass:
						classlist+=[row[0]]			#add people into class list
					insert_form.name = theclass			#add the class name in to the list of classes database
					insert_form.namelist = classlist		#add the people in the classlist into the namelist database
					
					insert_form.put()						#put into the form
				
			myform = Form.gql("WHERE name = '%s'"%(theclass)).get() # find the class of the student
			classlist=myform.namelist	#get the namelist of the class from the database
			name=users.get_current_user().nickname()[:-7]
			
		
			#open the form so as to be able to submit all my checkboxes
			self.response.out.write('''<div align = "left">
			<form action="/submit" method="post">''')		#"/submit" to submit
			self.response.out.write('''<table width=200 border = "1"><tr><td></td>''')
			
			titles = myform.titles
			counter=0
			for title in titles:
				self.response.out.write('''
				<td> %s </td>
				'''%(title))
			self.response.out.write('</tr>')
			for student in classlist: 
				self.response.out.write('''<tr><td>%s</td>''' % (student))
				
				editorcounter = 0
				for title in titles:
					exec('tick = myform.%s'%(title))
						
					if myform.editors[editorcounter] == user.nickname():
						disabled='' # allow editor to edit
					else:
						disabled='''disabled="true"'''
					if tick[counter] == 'yes':
						check='checked'
					else:
						check=''
					editorcounter+=1
					
					self.response.out.write('''<td><input name="%s" type="checkbox" %s value="yes" %s/></td>'''%((title+str(counter)),disabled,check))
					
				counter+=1	
				
				self.response.out.write('''</tr>''')
				#hide
			self.response.out.write('''<input type="hidden" name="student_class" value="%s"/>'''%(theclass))
					
				#submit
			self.response.out.write('''</tr></table><input type="submit" value="Update"></form></div>''')
					
			
			self.response.out.write('''
			<div>		
			<form method = "post" action="/create">
				<input type="hidden" name="student_class" value="%s" />
				<b>Name of new title</b><input type="text" name="new_title" placeholder="Please do not repeat." />
				<input type = "submit" value="Create"/>
			</form>
			</div>
			'''%(theclass))
			
		else:
			self.response.out.write('''<h4><a href = "%s" >LOGIN</a></h4>
		<div>
		<h2>Welcome to DHS L!ST <strong></strong>!</h2>
		<h3></h3>
		</div>''' % (users.create_login_url(self.request.uri)))
			self.response.out.write ('''</body></html>''')
class Submit(webapp.RequestHandler):
	def post(self):
		
		theclass=self.request.get('student_class')
		myform =Form.gql("WHERE name='%s' "%(theclass)).get()
		titles = myform.titles
		for title in titles:
			
			exec("checkbox=myform.%s"%(title))
			counter=0
			
			for tick in checkbox:
				
				message=self.request.get('%s'%(title+str(counter)))
				if message=='yes':
					
					checkbox[counter]='yes'
					
				counter+=1
			
		
		myform.put()
		self.redirect('/')
		

class Create (webapp.RequestHandler):
	def post(self):
		try:
			theclass=self.request.get('student_class')
			myform = Form.gql("WHERE name ='%s' "%(theclass)).get()	
			title=self.request.get('new_title')
			myform.titles+=[title]
			nonono=['no']*len(myform.namelist)		# initialize as no
			myform.editors+=[users.get_current_user().nickname()]
			exec('myform.%s = nonono'%(title))
			myform.put()
			self.redirect('/')
		except:
			self.response.out.write('Invalid list name.Try again.')
		
	
	
	
			
application = webapp.WSGIApplication([('/', MainPage),('/submit',Submit),('/create',Create)],debug=True)

def main():
  run_wsgi_app(application)
  

if __name__ == "__main__":
  main()