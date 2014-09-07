# -*- coding: utf-8 -*-

# Dear Me,
#	To continue development, you will need:
#	http://localhost:8080/video?vid=1
#	http://localhost/phpmyadmin/
#	https://developers.google.com/gdata/docs/2.0/basics
#	something about how to use google apps
#	love
# kthxbai

import web
import hashlib
import imghdr
import os
import datetime
import re

#to make sessions work
web.config.debug = False

urls = (
	'/', 'Start',			# the front page for logged-in users
	'/home', 'Home',		# the front page for logged-out users
	'/u', 'Profile',		# user profiles
	'/upload', 'Upload',	# upload video form and guidelines
	'/signup', 'Signup',		# info on the site and singup form
	'/logout', 'Logout',
	'/about', 'About',		# page with site info
	'/settings', 'Settings',	# settings page
	'/verify', 'Verify',
	'/video', 'Video'
	)
	
app = web.application(urls, globals())

session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'id': 0})

db = web.database(dbn='mysql', user='twouser', pw='user123', db='EnsiColab')

render = web.template.render("templates/", base='layout')

subjects = {"earlymath":"Iniciação à Matemática",
			"arithmetic":"Aritimética",
			"prealgebra":"Pré-Álgebra",
			"algebraone":"Álgebra I",
			"geometry":"Geometry",
			"algebratwo":"Álgebra II",
			"trigonometry":"Trigonometria",
			"probabilityandstatistics":"Probabilidade e Estatística",
			"precalculus":"Pré-Calculo",
			"differentialcalculus":"Cálculo Diferencial",
			"integralcalculus":"Cálculo Integral",
			"multivariablecalculus":"Cálculo Multivariável",
			"differentialequations":"Equações Diferenciais",
			"linearalgebra":"Álgebra Linear",
			"biology":"Biologia",
			"physics":"Física",
			"chemistry":"Química",
			"organicchemistry":"Química Orgânica",
			"astronomy":"Astronomia",
			"economy":"Economia",
			"entrepreneurship":"Empreendedorismo",
			"worldhistory":"História Geral",
			"brazilhistory":"História do Brasil",
			"arthistory":"História da Arte",
			"music":"Música",
			"philosophy":"Filosofia",
			"sociology":"Sociologia",
			"portuguese":"Língua Portuguesa",
			"literature":"Literatura",
			"essay":"Redação",
			"english":"Língua Inglesa",
			"computerscience":"Ciência da Computação",
			"other":"Outro",
			}


# classes of the actions
class Start:
	
	def GET(self):
		if session.id == 0:
			raise web.seeother("/home")
		
		# getting user info
		user_username = db.query("SELECT username FROM users WHERE userid=$id", vars={'id': session.id})
		username = user_username[0].username
		
		user_verified = db.query("SELECT verified FROM users WHERE userid=$id", vars={'id': session.id})
		verified = user_verified[0].verified
		
		user_profpic = db.query("SELECT profpic FROM users WHERE userid=$id", vars={'id': session.id})
		profpic = user_profpic[0].profpic
		profpicpath = "http://localhost:8080/" + profpic
		
		user_upvotes = db.query("SELECT upvotes FROM users WHERE userid=$id", vars={'id': session.id})
		upvotes = user_upvotes[0].upvotes
		
		user_downvotes = db.query("SELECT downvotes FROM users WHERE userid=$id", vars={'id': session.id})
		downvotes = user_downvotes[0].downvotes
		
		user_isteacher = db.query("SELECT isteacher FROM users WHERE userid=$id", vars={'id': session.id})
		isteacher = user_isteacher[0].isteacher
		
		user_educatedat = db.query("SELECT educated_at FROM users WHERE userid=$id", vars={'id': session.id})
		educatedat = user_educatedat[0].educated_at
		
		user_teachesat = db.query("SELECT teaches_at FROM users WHERE userid=$id", vars={'id': session.id})
		teachesat = user_teachesat[0].teaches_at
		
		profilelink = "/u?id=" + str(session.id)
		
		return render.start(username, verified, profpicpath, upvotes, downvotes, isteacher, educatedat, teachesat, profilelink)
	
	def POST(self):
		pass
		# code for handling any forms that Start may have

class Home:
	
	def GET(self, error_msg=None):
		if session.id != 0:
			raise web.seeother('/')
		
		return render.home(error_msg)
	
	def POST(self):
		# code for handling login form
		
		if session.id != 0:
			raise web.seeother('/')
			
		login_form = web.input()
		
		if not login_form.username_login:
			return render.home("Oops. Você esqueceu do usuário.")
		if not login_form.password_login:
			return render.home("Oops. Você esqueceu da senha.")
		
		# web.input() returned in unicode
		username_login = str(login_form.username_login)
		password_login = hashlib.md5(str(login_form.password_login)).hexdigest()
		
		results = db.query("SELECT userid FROM users WHERE username=$username AND pass=$password", vars={'username':username_login, 'password':password_login})
		
		if results:
			# At least one result found.
				
			id_login = results[0].userid
			# apparently I can't use results[0].id directly. it needs to be assigned.
			# after the first assignment, it destroys itself...
			
			if id_login != 0:
				session.id = id_login
				raise web.seeother("/")
		else:
			return self.GET("Oops... Usuário/Senha incorretos ou não existem.")
		
class Signup:

	def GET(self, error_msg=None):
		if session.id != 0:
			raise web.seeother('/')
			
		return render.signup(error_msg)
	
	def POST(self):
		# code for handling the signup form.
		
		if session.id != 0:
			raise web.seeother('/')
		
		form = web.input(profoualuno='')
			
		if not form.username:
			return self.GET("Oops. Você deve entrar um nome de usuário. Este é o nome que você usará para entrar no site.")
		
		if not form.password:
			return self.GET("Oops. Você deve entrar uma senha.")
		
		if not form.passwordconfirm:
			return self.GET("Oops. Você deve entrar a confirmação da senha. (é só repetir a senha que você já digitou.)")
			
		if not form.realname:
			return self.GET("Oops. Você deve entrar um Nome. Se não quiser dar seu nome real, fique à vontade para inventar um. Este nome será mostrado em seu perfil.")
		
		if not form.bio:
			return self.GET("Oops. Você deve entrar uma pequena bio. Digite algumas inforações sobre você. Se for já for formado em um curso de ensino superior, inclua o nome do curso.")
				
		if not form.profoualuno:
			return self.GET("Oops. Você deve selecionar uma opção (professor ou aluno).")
		
		if not form.education:
			education_signup = ""
		else:
			education_signup = str(form.education)
			
		if not form.job:
			job_signup = ""
		else:
			job_signup = str(form.job)
			
		username_signup = str(form.username)
		
		userexists = db.query("SELECT userid FROM users WHERE username=$username_signup", vars={'username_signup': username_signup})
		if userexists:
			return self.GET("Oops. Alguém já escolheu esse nome de usuário.")
		
		password_signup = hashlib.md5(str(form.password)).hexdigest()
		passwordconfirm_signup = hashlib.md5(str(form.passwordconfirm)).hexdigest()
		
		if password_signup != passwordconfirm_signup:
			return self.GET("Oops. Sua senha e sua confirmação de senha devem ser iguais.")
		
		realname_signup = str(form.realname)
		bio_signup = str(form.bio)
		
		if form.profoualuno == "professor":
			isteacher_signup = 1
		else:
			isteacher_signup = 0
		
		# All clear. Let's insert user
		
		db.query("INSERT INTO users \
		(username, pass, realname, bio, verified, upvotes, downvotes, isteacher, educated_at, teaches_at) \
		VALUES ($username, $password, $realname, $bio, $verified, $upvotes, $downvotes, $isteacher, $educated_at, $teaches_at)", \
		vars={'username':username_signup, 'password':password_signup, 'realname':realname_signup, 'bio':bio_signup, 'verified':0, 'upvotes':0, 'downvotes':0, 'isteacher':isteacher_signup, 'educated_at':education_signup, 'teaches_at':job_signup})
		
		# getting user id and setting session
		
		gotid = db.query("SELECT userid FROM users WHERE username=$username", vars={'username': username_signup})
		
		if not gotid:
				return "ERRO FATAL 1 (favor comunicar este erro ao administrador do site.)"
		else:
			id_signup = gotid[0].userid
			
			if id_signup != 0:
				session.id = id_signup
				newpath = ('static/users/' + str(session.id)) 
				if not os.path.exists(newpath): os.makedirs(newpath)
			
			else:
				return "ERRO FATAL 2 (favor comunicar este erro ao administrador do site.)"
		
		if session.id == 0:
			return "ERRO FATAL 2 (favor comunicar este erro ao administrador do site.)"
		
		profpic = web.input(photo={})
		
		photodir = "static/users/" + str(session.id)
		
		if not os.path.isdir(photodir):
			os.mkdir(photodir)
		
		if 'photo' in profpic: # checking if file-object is created
			
			if not profpic.photo.value:
				return self.GET()
			
			photopath = profpic.photo.filename.replace('\\','/') # replaces windows-style slashes with linux ones
			photoname = photopath.split('/')[-1] # is file name with extension.
			
			oldfilequery = db.query("SELECT profpic FROM users WHERE userid=$id", vars={'id': session.id})
			oldfile = oldfilequery[0].profpic
			
			if not oldfile == "static/NoPic.gif":
				# deleting the old file, if it exists
				if os.path.isfile(oldfile):
					os.remove(oldfile)
			
			phototype = imghdr.what(photoname, profpic.photo.value)
			
			isok = 0
			filetypes = ('jpeg', 'tiff', 'bmp', 'png')
			for filetype in filetypes:
				if phototype == filetype:
					isok = 1
					break
			
			if not isok:
				filestring = filetypes[0]
				for filetype in filetypes[1:]:
					filestring = filestring + ", " + filetype
					
				return self.GET("Oops. O arquivo deve ser do tipo: %s" % (filestring))
			
			fout = open(photodir +'/'+ photoname, 'wb') #file to store the uploaded photo
			fout.write(profpic.photo.file.read()) # writes uploaded to fout
			fout.close() #upload complete
			
			newfilequery = db.query("UPDATE users SET profpic=$newpath WHERE userid=$id", vars={'newpath': (photodir +'/'+ photoname), 'id': session.id})
			
			return self.GET()
		else:
			return self.GET("Oops. ocorreu um erro ao realizar o upload.")
		
class Logout:
	def GET(self):
		if session.id != 0:
			session.kill()
		raise web.seeother('/home')
		
class About:
	def GET(self, item=None):
		# item can be:
		#	verify (what it is and how to request it)
		#	username (what it is used for)
		#	password (recommendations)
		#	accounttype (why there's a diff and why cant be altered)
		#	name (how it can be invented, if worried about privacy)
		#	bio (what should be in it)
		#	education (why this is here, and if privacy, invent it (dont use real names if so))
		#	job (why this is here, and if privacy, invent it (dont use real names if so). and why its only for teachers)
		#	profpic (what it is used for, assurance that it will never be kept if they delete it and that they can use any pic they want, or none, if thats what they want)
		#	uploading (tips for uploading, how to upload, how to film, guidelines, protecting students' images, etc)
		#	youtubeupload
		#	youtubelink (once it uploads, how to get the link to post here)
		#	guidelines for filming, privacy of students, etc
		#	creativecommons
		
		return render.about()
		
class Settings:
	def GET(self, error_msg=None, success=None):
		if session.id == 0:
			raise web.seeother('/home')
		
		# getting user info
		user_username = db.query("SELECT username FROM users WHERE userid=$id", vars={'id': session.id})
		username = user_username[0].username
		
		user_realname = db.query("SELECT realname FROM users WHERE userid=$id", vars={'id': session.id})
		realname = user_realname[0].realname
		
		user_bio = db.query("SELECT bio FROM users WHERE userid=$id", vars={'id': session.id})
		bio = user_bio[0].bio
		
		user_verified = db.query("SELECT verified FROM users WHERE userid=$id", vars={'id': session.id})
		verified = user_verified[0].verified
		
		requested_verification = False
		
		if not verified:
			already_requested = db.query("SELECT email FROM verification_requests WHERE userid=$id", vars={'id': session.id})
			if already_requested:
				requested_verification = True
		
		user_profpic = db.query("SELECT profpic FROM users WHERE userid=$id", vars={'id': session.id})
		profpic = user_profpic[0].profpic
		profpicpath = "http://localhost:8080/" + profpic
		
		user_upvotes = db.query("SELECT upvotes FROM users WHERE userid=$id", vars={'id': session.id})
		upvotes = user_upvotes[0].upvotes
		
		user_downvotes = db.query("SELECT downvotes FROM users WHERE userid=$id", vars={'id': session.id})
		downvotes = user_downvotes[0].downvotes
		
		user_isteacher = db.query("SELECT isteacher FROM users WHERE userid=$id", vars={'id': session.id})
		isteacher = user_isteacher[0].isteacher
		
		user_educatedat = db.query("SELECT educated_at FROM users WHERE userid=$id", vars={'id': session.id})
		educatedat = user_educatedat[0].educated_at
		
		user_teachesat = db.query("SELECT teaches_at FROM users WHERE userid=$id", vars={'id': session.id})
		teachesat = user_teachesat[0].teaches_at
		
		profilelink = "/u?id=" + str(session.id)
		
		return render.settings(username, realname, bio, verified, profpic, upvotes, downvotes, isteacher, educatedat, teachesat, profilelink, error_msg, success, requested_verification)
		
		
	def POST(self):
		if session.id == 0:
			raise web.seeother('/home')
		
		form = web.input(submit_username=None, submit_name=None, submit_password=None, submit_bio=None, submit_education=None, submit_job=None, verify_settings=None, delete_profpic=None, submit_profpic=None)
		# use "if form.submit_username:" to check which form user pressed...
		
		if form.submit_name: # for altering the Real Name
			if not form.name_settings:
				return self.GET("Oops. Você esqueceu de digitar um novo nome.", None)
			db.query("UPDATE users SET realname=$newname WHERE userid=$id", vars={'newname': str(form.name_settings), 'id': session.id})
			return self.GET(None, "Nome atualizado com sucesso")
		
		if form.submit_username:
			if not form.username_settings:
				return self.GET("Oops. Você esqueceu de digitar um novo nomede usuário.", None)
			
			form_username = str(form.username_settings)
			user_exists_query = db.query("SELECT userid FROM users WHERE username=$username", vars={'username': form_username})
			
			if user_exists_query:
				if user_exists_query[0].userid == session.id:
					return self.GET("Oops. Esse já é o seu nome de usuário.", None)
				elif user_exists_query[0].userid != session.id:
					return self.GET("Oops. Esse nome de usuário já foi escolhido por outra pessoa.", None)
			
			result = db.query("UPDATE users SET username=$newusername WHERE userid=$userid", vars={'newusername': form_username, 'userid': session.id})
			
			if not result:
				return self.GET("FATAL DATABASE ERROR 3", None)
			else:
				return self.GET(None, "Nome de usuário atualizado com sucesso!")
		
		if form.submit_bio:
			if not form.bio_settings:
				return self.GET("Oops. Você esqueceu de digitar uma nova bio.", None)
			
			form_bio = str(form.bio_settings)
			
			result = db.query("UPDATE users SET bio=$newbio WHERE userid=$userid", vars={'newbio': form_bio, 'userid': session.id})
			
			if not result:
				return self.GET("FATAL DATABASE ERROR 4", None)
			else:
				return self.GET(None, "Bio atualizada com sucesso!")
			
		if form.submit_education:
			if not form.education_settings:
				return self.GET("Oops. Você esqueceu de digitar uma instituição de formação.", None)
			form_education = str(form.education_settings)
			result = db.query("UPDATE users SET educated_at=$neweducation WHERE userid=$userid", vars={'neweducation': form_education, 'userid': session.id})
			
			if not result:
				return self.GET("FATAL DATABASE ERROR 5", None)
			else:
				return self.GET(None, "Instituição de Formação atualizada com sucesso!")
			
		if form.submit_job:
			if not form.job_settings:
				return self.GET("Oops. Você esqueceu de digitar uma instituição de trabalho.", None)
			form_job = str(form.job_settings)
			result = db.query("UPDATE users SET teaches_at=$newjob WHERE userid=$userid", vars={'newjob': form_job, 'userid': session.id})
			
			if not result:
				return self.GET("FATAL DATABASE ERROR 6", None)
			else:
				return self.GET(None, "Instituição de Trabalho atualizada com sucesso!")
		
		if form.submit_password:
			if not form.oldpassword_settings:
				return self.GET("Oops. Você esqueceu de digitar sua senha atual.", None)
			if not form.password_settings:
				return self.GET("Oops. Você esqueceu de digitar uma nova senha.", None)
			if not form.passwordconfirm_settings:
				return self.GET("Oops. Você esqueceu de digitar a confirmação de senha.", None)
			
			oldpassword = hashlib.md5(str(form.oldpassword_settings)).hexdigest()
			newpassword = hashlib.md5(str(form.password_settings)).hexdigest()
			confirmpassword = hashlib.md5(str(form.passwordconfirm_settings)).hexdigest()
			
			isauth = db.query("SELECT username FROM users WHERE userid=$userid AND pass=$oldpass", vars={'userid': session.id, 'oldpass': oldpassword})
			
			if not isauth:
				return self.GET("Oops. Sua senha atual está incorreta.", None)
			else:
				if newpassword != confirmpassword:
					return self.GET("Oops. Sua nova senha deve ser igual à sua confirmação de senha.", None)
				
				result = db.query("UPDATE users SET pass=$newpass WHERE userid=$userid", vars={'newpass': newpassword, 'userid': session.id})
				if not result:
					return self.GET("FATAL DATABASE ERROR 5", None)
				else:
					return self.GET(None, "Senha atualizada com sucesso!")
		
		if form.verify_settings:
			already_verified = db.query("SELECT verified FROM users WHERE userid=$id", vars={'id': session.id})
			if already_verified and already_verified[0].verified == 1:
				return self.GET("Oops. Você já foi verificado como professor.", None)
			
			already_requested = db.query("SELECT email FROM verification_requests WHERE userid=$id", vars={'id': session.id})
			if already_requested:
				return self.GET("Oops. Você já pediu para ser verificado. Siga as <a href='/about?i=verify'>instruções de verificação</a>.", None)
		
			raise web.seeother("/verify")
		
		if form.submit_profpic:
			profpic = web.input(photo={})
		
			photodir = "static/users/" + str(session.id)
		
			if not os.path.isdir(photodir):
				os.mkdir(photodir)
		
			if 'photo' in profpic: # checking if file-object is created
			
				if not profpic.photo.value:
					return self.GET("Oops. Você deve escolher uma foto para atualizar", None)
			
				photopath = profpic.photo.filename.replace('\\','/') # replaces windows-style slashes with linux ones
				photoname = photopath.split('/')[-1] # is file name with extension.
			
				oldfilequery = db.query("SELECT profpic FROM users WHERE userid=$id", vars={'id': session.id})
				oldfile = oldfilequery[0].profpic
			
				if not oldfile == "static/NoPic.gif":
					# deleting the old file, if it exists
					if os.path.isfile(oldfile):
						os.remove(oldfile)
			
				phototype = imghdr.what(photoname, profpic.photo.value)
			
				isok = 0
				filetypes = ('jpeg', 'tiff', 'bmp', 'png')
				for filetype in filetypes:
					if phototype == filetype:
						isok = 1
						break
			
				if not isok:
					filestring = filetypes[0]
					for filetype in filetypes[1:]:
						filestring = filestring + ", " + filetype
					
					return self.GET("Oops. O arquivo deve ser do tipo: %s" % (filestring))
				
				fout = open(photodir +'/'+ photoname, 'wb') #file to store the uploaded photo
				fout.write(profpic.photo.file.read()) # writes uploaded to fout
				fout.close() #upload complete
				
				newfilequery = db.query("UPDATE users SET profpic=$newpath WHERE userid=$id", vars={'newpath': (photodir +'/'+ photoname), 'id': session.id})
				
				return self.GET(None, "Foto de Perfil atualizada com sucesso!")
		
		if form.delete_profpic:
			
			photodir_query = db.query("SELECT profpic FROM users WHERE userid=$id", vars={'id': session.id})
			photodir = photodir_query[0].profpic
			
			if photodir == "static/NoPic.gif":
				return self.GET("Oops. Você não tem uma foto de perfil que possa aser excluída.", None)
			if os.path.isfile(photodir):
				os.remove(photodir)
			
			db.query("UPDATE users SET profpic=$defaultpath WHERE userid=$id", vars={'defaultpath': 'static/NoPic.gif', 'id': session.id})
			
			return self.GET(None, "Foto de Perfil excluída com sucesso!")

class Verify:
	def GET(self, error_msg=None):
		if session.id == 0:
			raise web.seeother('/home')
			
		already_verified = db.query("SELECT verified FROM users WHERE userid=$id", vars={'id': session.id})
		if already_verified and already_verified[0].verified == 1:
			return render.alreadyverified()
		
		already_requested = db.query("SELECT email FROM verification_requests WHERE userid=$id", vars={'id': session.id})
		if already_requested:
			return render.alreadyrequested()
		
		return render.requestemail(error_msg=None)
	
	def POST(self):
		if session.id == 0:
			raise web.seeother('/home')
			
		already_verified = db.query("SELECT verified FROM users WHERE userid=$id", vars={'id': session.id})
		if already_verified and already_verified[0].verified == 1:
			return render.alreadyverified()
		
		already_requested = db.query("SELECT email FROM verification_requests WHERE userid=$id", vars={'id': session.id})
		if already_requested:
			return render.alreadyrequested()
		
		form = web.input(email_verify=None)
		
		if not form.email_verify:
			return self.GET("Oops. Você deve digitar um endereço de email.")
			
		email_verify = form.email_verify
		
		db.query("INSERT INTO verification_requests (userid, email) VALUES ($userid, $email)", vars={'userid': session.id, 'email': email_verify})
		raise web.seeother('/verify')
		

class Upload:
	def GET(self, error_msg=None, success=None):
		if session.id == 0:
			raise web.seeother("/home")
		
		# getting user info
		user_username = db.query("SELECT username FROM users WHERE userid=$id", vars={'id': session.id})
		username = user_username[0].username
		
		user_verified = db.query("SELECT verified FROM users WHERE userid=$id", vars={'id': session.id})
		verified = user_verified[0].verified
		
		user_profpic = db.query("SELECT profpic FROM users WHERE userid=$id", vars={'id': session.id})
		profpic = user_profpic[0].profpic
		profpicpath = "http://localhost:8080/" + profpic
		
		user_upvotes = db.query("SELECT upvotes FROM users WHERE userid=$id", vars={'id': session.id})
		upvotes = user_upvotes[0].upvotes
		
		user_downvotes = db.query("SELECT downvotes FROM users WHERE userid=$id", vars={'id': session.id})
		downvotes = user_downvotes[0].downvotes
		
		user_isteacher = db.query("SELECT isteacher FROM users WHERE userid=$id", vars={'id': session.id})
		isteacher = user_isteacher[0].isteacher
		
		user_educatedat = db.query("SELECT educated_at FROM users WHERE userid=$id", vars={'id': session.id})
		educatedat = user_educatedat[0].educated_at
		
		user_teachesat = db.query("SELECT teaches_at FROM users WHERE userid=$id", vars={'id': session.id})
		teachesat = user_teachesat[0].teaches_at
		
		profilelink = "/u?id=" + str(session.id)
		
		return render.upload(username, verified, profpicpath, upvotes, downvotes, isteacher, educatedat, teachesat, profilelink, error_msg, success)
		
	def POST(self):
		if session.id == 0:
			raise web.seeother("/home")
		
		form = web.input(subject='', isCC=None)
		
		if not form.subject:
			return self.GET("Oops. Você esqueceu de selecionar uma matéria.", None)
			
		if not form.videolink:
			return self.GET("Oops. Você esqueceu de entrar o link para a vídeo-aula.", None)
			
		if not form.videoname:
			return self.GET("Oops. Você esqueceu de digitar o nome da vídeo aula.", None)
			
		if not form.videodescription:
			return self.GET("Oops. Você esqueceu de digitar uma descrição da vídeo-aula.", None)
			
		listoftopics = []
		
		if form.topicone:
			listoftopics.append(form.topicone)
		if form.topictwo:
			listoftopics.append(form.topictwo)
		if form.topicthree:
			listoftopics.append(form.topicthree)
		if form.topicfour:
			listoftopics.append(form.topicfour)
		if form.topicfive:
			listoftopics.append(form.topicfive)
		
		istheretopic = 0
		if listoftopics:
			istheretopic = 1
		
		for topic in listoftopics:
			#see if topic is in the topiclist table
			topicexists = db.query("SELECT topicid FROM topiclist WHERE topicname=$topicname", vars={'topicname': topic})	
			if not topicexists:
				#put the topic in the topiclist table
				db.query("INSERT INTO topiclist (topicname) VALUES ($topicname)", vars={'topicname':topic})
		
		isCC = 0
		if form.isCC:
			isCC = 1
		
		# get datetime, store in var called datetime_string. With the +10s, all the fields are at least two digits long (dates can, then, be compared as numbers)
		i = datetime.datetime.now()
		datetime_string = str(i.year) + str(i.month + 10) + str(i.day + 10) + str(i.hour + 10) + str(i.minute + 10) + str(i.second + 10)
		
		# check if the YouTube link is valid (use YouTube API.) ### WHILE THIS PART ISNT CODED, ILL ASSUME THE USER IS NICE
		
		db.query("INSERT INTO videos \
		(userid, videoname, videolink, videodescription, istheretopic, subject, upvotes, downvotes, isCC, isreported, datetime) \
		VALUES ($userid, $videoname, $videolink, $videodescription, $istheretopic, $subject, $upvotes, $downvotes, $isCC, $isreported, $datetime)", \
		vars={'userid':session.id, 'videoname':form.videoname, 'videolink':form.videolink, 'videodescription':form.videodescription, 'istheretopic':istheretopic, 'subject':form.subject, 'upvotes':0, 'downvotes':0, 'isCC':isCC, 'isreported':0, 'datetime':datetime_string})
		
		added_id = db.query("SELECT videoid FROM videos WHERE userid=$userid AND datetime=$datetime", vars={'userid':session.id, 'datetime':datetime_string})
		
		if not added_id:
			return self.GET("Oops. O vídeo foi inserido no banco de dados com sucesso, mas não foi possível localizá-lo para inserir seus tópicos... (ERROR 14)", None)
		else:
			addedvideoid = added_id[0].videoid
			for topic in listoftopics:
				db.query("INSERT INTO topics (videoid, topicname) VALUES ($videoid, $topicname)", vars={'videoid': addedvideoid, 'topicname': topic})
		
		return self.GET(None, "Vídeo foi inserido no banco de dados com sucesso!")

class Video:
	def GET(self, error_msg=None, success=None, video_id=None):
		if session.id == 0:
			raise web.seeother("/home")
		
		# getting user info
		user_username = db.query("SELECT username FROM users WHERE userid=$id", vars={'id': session.id})
		username = user_username[0].username
		user_verified = db.query("SELECT verified FROM users WHERE userid=$id", vars={'id': session.id})
		verified = user_verified[0].verified
		user_profpic = db.query("SELECT profpic FROM users WHERE userid=$id", vars={'id': session.id})
		profpic = user_profpic[0].profpic
		profpicpath = "http://localhost:8080/" + profpic
		user_upvotes = db.query("SELECT upvotes FROM users WHERE userid=$id", vars={'id': session.id})
		upvotes = user_upvotes[0].upvotes
		user_downvotes = db.query("SELECT downvotes FROM users WHERE userid=$id", vars={'id': session.id})
		downvotes = user_downvotes[0].downvotes
		user_isteacher = db.query("SELECT isteacher FROM users WHERE userid=$id", vars={'id': session.id})
		isteacher = user_isteacher[0].isteacher
		user_educatedat = db.query("SELECT educated_at FROM users WHERE userid=$id", vars={'id': session.id})
		educatedat = user_educatedat[0].educated_at
		user_teachesat = db.query("SELECT teaches_at FROM users WHERE userid=$id", vars={'id': session.id})
		teachesat = user_teachesat[0].teaches_at
		profilelink = "/u?id=" + str(session.id)
		
		# getting the video id from the get form
		getinput = web.input(vid=None)
		
		if not getinput.vid and not video_id:
			raise web.seeother("/home")
		
		if not getinput.vid and video_id:
			videoid = video_id
		else:
			videoid = getinput.vid
		
		vid_posterid = db.query("SELECT userid FROM videos WHERE videoid=$id", vars={'id': videoid})
		posterid = vid_posterid[0].userid
		vid_videoname = db.query("SELECT videoname FROM videos WHERE videoid=$id", vars={'id': videoid})
		videoname = vid_videoname[0].videoname
		vid_videolink = db.query("SELECT videolink FROM videos WHERE videoid=$id", vars={'id': videoid})
		videolink = vid_videolink[0].videolink
		vid_videodescription = db.query("SELECT videodescription FROM videos WHERE videoid=$id", vars={'id': videoid})
		videodescription = vid_videodescription[0].videodescription
		vid_istheretopic = db.query("SELECT istheretopic FROM videos WHERE videoid=$id", vars={'id': videoid})
		istheretopic = vid_istheretopic[0].istheretopic
		vid_subject = db.query("SELECT subject FROM videos WHERE videoid=$id", vars={'id': videoid})
		subject = vid_subject[0].subject
		subject = subjects[subject]
		vid_videoupvotes = db.query("SELECT upvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
		videoupvotes = vid_videoupvotes[0].upvotes
		vid_videodownvotes = db.query("SELECT downvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
		videodownvotes = vid_videodownvotes[0].downvotes
		vid_isCC = db.query("SELECT isCC FROM videos WHERE videoid=$id", vars={'id': videoid})
		isCC = vid_isCC[0].isCC
		vid_isreported = db.query("SELECT isreported FROM videos WHERE videoid=$id", vars={'id': videoid})
		isreported = vid_isreported[0].isreported
		vid_datetime = db.query("SELECT datetime FROM videos WHERE videoid=$id", vars={'id': videoid})
		datetime = vid_datetime[0].datetime
		
		datetime = unicode(str(int(datetime[6] + datetime[7]) - 10), "utf-8") + u'/' + unicode(str(int(datetime[4] + datetime[5]) - 10), "utf-8") + u'/' + datetime[0] + datetime[1] + datetime[2] + datetime[3] + u' \u00E0s ' + unicode(str(int(datetime[8] + datetime[9]) - 10), "utf-8") + u':' + unicode(str(int(datetime[10] + datetime[11]) - 10), "utf-8")
		
		#with the video link see if the video exists. If not, display error message (render video not found page) ### WHILE THIS IS NOT CODED, ILL ASSUME THE VIDEO EXISTS
		
		#if the video exists, get video id.
		youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
		youtube_regex_match = re.match(youtube_regex, videolink)
		if youtube_regex_match:
			videolinkid = youtube_regex_match.group(6)
		else:
			return "Invalid link - ERROR 15"
		
		#getting the embed version of the video.
		videoembed = "<iframe width='900' height='506' src='//www.youtube.com/embed/" + videolinkid + "?autoplay=1' frameborder='0' allowfullscreen></iframe>"
		
		#get viewcount from youtube api
		viewcount = 100
		
		#get the topics and put them in list.
		topiclist=[]
		if istheretopic:
			topicsquery = db.query("SELECT topicname FROM topics WHERE videoid=$id", vars={'id': videoid})
			for topicrow in topicsquery:
				topiclist.append(topicrow.topicname)
		
		#use the isreported to see if the video has many reports. If so, check if it's already in the "process reported" table. if not, insert it there.
		
		#getting poster info
		poster_username = db.query("SELECT username FROM users WHERE userid=$id", vars={'id': posterid})
		posterusername = poster_username[0].username
		poster_verified = db.query("SELECT verified FROM users WHERE userid=$id", vars={'id': posterid})
		posterverified = poster_verified[0].verified
		poster_profpic = db.query("SELECT profpic FROM users WHERE userid=$id", vars={'id': posterid})
		posterprofpic = poster_profpic[0].profpic
		posterprofpicpath = "http://localhost:8080/" + posterprofpic
		poster_isteacher = db.query("SELECT isteacher FROM users WHERE userid=$id", vars={'id': posterid})
		posteristeacher = poster_isteacher[0].isteacher
		poster_educatedat = db.query("SELECT educated_at FROM users WHERE userid=$id", vars={'id': posterid})
		postereducatedat = poster_educatedat[0].educated_at
		poster_teachesat = db.query("SELECT teaches_at FROM users WHERE userid=$id", vars={'id': posterid})
		posterteachesat = poster_teachesat[0].teaches_at
		posterprofilelink = "/u?id=" + str(posterid)
		
		#see if user already upvoted. if so, change the var isupvote to 1 or 0
		didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
		
		isupvote = 0
		if didvote:
			isupvote_q = db.query("SELECT isupvote FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
			isupvote = isupvote_q[0].isupvote
		
		return render.video(username, verified, profpicpath, upvotes, downvotes, isteacher, educatedat, teachesat, profilelink, error_msg, success, videoname, videoembed, videodescription, subject, videoupvotes, videodownvotes, isCC, datetime, topiclist, posterusername, posterverified, posterprofpicpath, posteristeacher, postereducatedat, posterteachesat, posterprofilelink, videoid, viewcount, didvote, isupvote)
	
	def POST(self):
		#handle upvoting, downvoting and undoing these for the video...
		if session.id == 0:
			raise web.seeother("/home")
			
		form = web.input(upvotevideo=None, downvotevideo=None, un_upvotevideo=None, un_downvotevideo=None)
		
		if form.upvotevideo:
			videoid = form.videoid
			
			#see if user already upvoted. if so, change the var isupvote to 1 or 0
			didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
		
			isupvote = 0
			if didvote:
				isupvote_q = db.query("SELECT isupvote FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
				isupvote = isupvote_q[0].isupvote
				
				if isupvote:
					return self.GET("Você já votou a favor deste vídeo", None)
				else:
					deletecurrentvote = db.query("DELETE FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
					
					#update the videos table
					vid_videodownvotes = db.query("SELECT downvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
					videodownvotes = vid_videodownvotes[0].downvotes
					videodownvotes -= 1
					vid_videodownvotes = db.query("UPDATE videos SET downvotes=$newdownvotes WHERE videoid=$id", vars={'id': videoid, 'newdownvotes': videodownvotes})
					
					didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
					
					if didvote:
						return "FATAL ERROR 16"
					else:
						insertvote = db.query("INSERT INTO videovotes (videoid, userid, isupvote) VALUES ($videoid, $id, $isupvote)", vars={'videoid': videoid, 'id': session.id, 'isupvote': 1})
						
						#update the videos table
						vid_videoupvotes = db.query("SELECT upvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
						videoupvotes = vid_videoupvotes[0].upvotes
						videoupvotes += 1
						vid_videoupvotes = db.query("UPDATE videos SET upvotes=$newupvotes WHERE videoid=$id", vars={'id': videoid, 'newupvotes': videoupvotes})
						
						
						if insertvote:
							return self.GET(None, None, videoid)
						else:
							return "FATAL ERROR 17"
			
			else:
				insertvote = db.query("INSERT INTO videovotes (videoid, userid, isupvote) VALUES ($videoid, $id, $isupvote)", vars={'videoid': videoid, 'id': session.id, 'isupvote': 1})
				
				#update the videos table
				vid_videoupvotes = db.query("SELECT upvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
				videoupvotes = vid_videoupvotes[0].upvotes
				videoupvotes += 1
				vid_videoupvotes = db.query("UPDATE videos SET upvotes=$newupvotes WHERE videoid=$id", vars={'id': videoid, 'newupvotes': videoupvotes})
				
				if insertvote:
					return self.GET(None, None, videoid)
				else:
					return "FATAL ERROR 17"
		
		if form.downvotevideo:
			videoid = form.videoid
			
			#see if user already upvoted. if so, change the var isupvote to 1 or 0
			didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
		
			isupvote = 0
			if didvote:
				isupvote_q = db.query("SELECT isupvote FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
				isupvote = isupvote_q[0].isupvote
				
				if isupvote:
					deletecurrentvote = db.query("DELETE FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
					
					#update the videos table
					vid_videoupvotes = db.query("SELECT upvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
					videoupvotes = vid_videoupvotes[0].upvotes
					videoupvotes -= 1
					vid_videoupvotes = db.query("UPDATE videos SET upvotes=$newupvotes WHERE videoid=$id", vars={'id': videoid, 'newupvotes': videoupvotes})
					
					didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
					
					if didvote:
						return "FATAL ERROR 16"
					else:
						insertvote = db.query("INSERT INTO videovotes (videoid, userid, isupvote) VALUES ($videoid, $id, $isupvote)", vars={'videoid': videoid, 'id': session.id, 'isupvote': 0})
						
						#update the videos table
						vid_videodownvotes = db.query("SELECT downvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
						videodownvotes = vid_videodownvotes[0].downvotes
						videodownvotes += 1
						vid_videodownvotes = db.query("UPDATE videos SET downvotes=$newdownvotes WHERE videoid=$id", vars={'id': videoid, 'newdownvotes': videodownvotes})
						
						
						if insertvote:
							return self.GET(None, None, videoid)
						else:
							return "FATAL ERROR 17"
				else:
					return self.GET("Você já votou contra este vídeo", None)
					
			else:
				insertvote = db.query("INSERT INTO videovotes (videoid, userid, isupvote) VALUES ($videoid, $id, $isupvote)", vars={'videoid': videoid, 'id': session.id, 'isupvote': 0})
				
				#update the videos table
				vid_videodownvotes = db.query("SELECT downvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
				videodownvotes = vid_videodownvotes[0].downvotes
				videodownvotes += 1
				vid_videodownvotes = db.query("UPDATE videos SET downvotes=$newdownvotes WHERE videoid=$id", vars={'id': videoid, 'newdownvotes': videodownvotes})
				
				if insertvote:
					return self.GET(None, None, videoid)
				else:
					return "FATAL ERROR 21"
		
		if form.un_upvotevideo:
			videoid = form.videoid
			
			#see if user already upvoted. if so, change the var isupvote to 1 or 0
			didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
			
			isupvote = 0
			if didvote:
				isupvote_q = db.query("SELECT isupvote FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
				isupvote = isupvote_q[0].isupvote
				
				if isupvote:
					deletecurrentvote = db.query("DELETE FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
					
					#update the videos table
					vid_videoupvotes = db.query("SELECT upvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
					videoupvotes = vid_videoupvotes[0].upvotes
					videoupvotes -= 1
					vid_videoupvotes = db.query("UPDATE videos SET upvotes=$newupvotes WHERE videoid=$id", vars={'id': videoid, 'newupvotes': videoupvotes})
					
					didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
					
					if didvote:
						return "FATAL ERROR 19"
					else:
						return self.GET(None, None, videoid)
				else:
					return "FATAL ERROR 18"
		
			else:
				return "FATAL ERROR 22"
		
		if form.un_downvotevideo:
			videoid = form.videoid
			
			#see if user already upvoted. if so, change the var isupvote to 1 or 0
			didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
			
			isupvote = 0
			if didvote:
				isupvote_q = db.query("SELECT isupvote FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
				isupvote = isupvote_q[0].isupvote
				
				if isupvote:
					return "FATAL ERROR 23"
				else:
					deletecurrentvote = db.query("DELETE FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
					
					#update the videos table
					vid_videodownvotes = db.query("SELECT downvotes FROM videos WHERE videoid=$id", vars={'id': videoid})
					videodownvotes = vid_videodownvotes[0].downvotes
					videodownvotes -= 1
					vid_videodownvotes = db.query("UPDATE videos SET downvotes=$newdownvotes WHERE videoid=$id", vars={'id': videoid, 'newdownvotes': videodownvotes})
					
					didvote = db.query("SELECT voteid FROM videovotes WHERE videoid=$videoid AND userid=$id", vars={'id': session.id, 'videoid': videoid})
					
					if didvote:
						return "FATAL ERROR 24"
					else:
						return self.GET(None, None, videoid)
		
			else:
				return "FATAL ERROR 25"
		
def notfound():
	return web.notfound(render.notfound())
app.notfound = notfound

if __name__ == "__main__":
	app.run()
