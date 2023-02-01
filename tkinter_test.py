import hashlib
import sqlite3
import tkinter as tk
from tkPDFViewer import tkPDFViewer as pdf


LARGE_FONT = ("Verdana", 12)
connection_obj = sqlite3.connect('users.db')
cursor_obj = connection_obj.cursor()


class GUI(tk.Tk):

	def __init__(self, *args, **kwargs):

		tk.Tk.__init__(self, *args, **kwargs)
		container = tk.Frame(self)
		self.winfo_toplevel().title("CS Revise")
		self.winfo_toplevel().geometry("600x600")
		container.pack(side="top", fill="both", expand=True)

		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		self.frames = {}

		for F in (LoginPage, PageRegister, StartPage, MainPage, Alevel, Gcse, Cs, Algorithms, cs1, Quiz1, Revise1):

			frame = F(container, self)

			self.frames[F] = frame

			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame(StartPage)

	def show_frame(self, cont):

		frame = self.frames[cont]
		frame.tkraise()

	def register_user(self, username_entry, password1_entry, password2_entry,
					email_entry, username, password1, password2, email):

		username_info = username.get()
		password1_info = password1.get()
		password2_info = password2.get()
		email_info = email.get()

		# checks if all the fields are filled
		if username_info and password1_info and password2_info and email_info:
			# checks if username exists, all usernames must be different
			if cursor_obj.execute('''SELECT Username FROM USERS WHERE Username=?''', (username_info,)).fetchone():
				username_exists_message = tk.Label(self, text="Username already in use!", fg="red")
				username_exists_message.pack(pady=10)
				self.after(4000, lambda: username_exists_message.destroy())
				username_entry.delete(0, tk.END)
			else:
				# checks if passwords match
				if password2_info == password1_info:
					hashed = hashlib.sha256(str(password1_info).encode('utf-8')).hexdigest()
					cursor_obj.execute(''' INSERT INTO USERS(Username, Email, Password) VALUES(?,?,?) ''', (
						username_info,
						email_info,
						hashed))
					connection_obj.commit()
					successful_registration = tk.Label(self, text="Registration success", fg="green")
					successful_registration.pack(pady=10)
					self.after(4000, lambda: successful_registration.destroy())
					username_entry.delete(0, tk.END)
					password1_entry.delete(0, tk.END)
					password2_entry.delete(0, tk.END)
					email_entry.delete(0, tk.END)
				else:
					password_dont_match_message = tk.Label(self, text="Passwords don't match!", fg="red")
					password_dont_match_message.pack(pady=10)
					self.after(4000, lambda: password_dont_match_message.destroy())
					password1_entry.delete(0, tk.END)
					password2_entry.delete(0, tk.END)

		else:
			empty_field_message = tk.Label(self, text="All of the fields must be filled", fg="red")
			empty_field_message.pack(pady=10)
			self.after(4000, lambda: empty_field_message.destroy())

	def login_user(self, email_login, password_login, login_email_entry, login_password_entry):
		email_info = email_login.get()
		password_info = password_login.get()
		hashed = hashlib.sha256(str(password_info).encode('utf-8')).hexdigest()
		query_to_receive_info_of_the_user = """SELECT Email, Password FROM 
		USERS WHERE Email=? AND Password=?"""
		if cursor_obj.execute(query_to_receive_info_of_the_user, (email_info, hashed)).fetchone():
			self.show_frame(MainPage)
		else:
			login_email_entry.delete(0, tk.END)
			login_password_entry.delete(0, tk.END)
			incorrect_credential_message = tk.Label(self, text="Incorrect credentials! Please check the information.", fg="red")
			incorrect_credential_message.pack(pady=10)
			self.after(4000, lambda: incorrect_credential_message.destroy())


class LoginPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)

		email_login = tk.StringVar()
		password_login = tk.StringVar()
		label1 = tk.Label(self, text="Enter your details", font=50)
		label1.pack(padx=30, pady=30)

		label_login_email = tk.Label(self, text="Email:", font=30)
		label_login_email.pack(pady=10)
		login_email_entry = tk.Entry(self, textvariable=email_login, width=30)
		login_email_entry.pack()
		label_password = tk.Label(self, text="Password:", font=30)
		label_password.pack(pady=10)
		login_password_entry = tk.Entry(self, textvariable=password_login, width=30, show="*")
		login_password_entry.pack()
		login_button = tk.Button(self, width=10, height=2, bg="cyan", text="Login",
								 command=lambda: controller.login_user(email_login, password_login,
																	   login_email_entry, login_password_entry))
		login_button.pack(padx=10, pady=10)

		button1 = tk.Button(self, text="Back to home", command=lambda: controller.show_frame(StartPage))

		button1.pack(pady=100)


class PageRegister(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)

		self.winfo_toplevel().geometry("600x600")
		username = tk.StringVar()
		password1 = tk.StringVar()
		password2 = tk.StringVar()
		email = tk.StringVar()

		tk.Label(self, text="Please enter details below to register", font=30).pack(padx=10, pady=20)
		tk.Label(self, text="").pack()
		tk.Label(self, text="Email * ").pack()
		email_entry = tk.Entry(self, textvariable=email, width=30)
		email_entry.pack()
		tk.Label(self, text="Username *").pack()
		username_entry = tk.Entry(self, textvariable=username, width=30)
		username_entry.pack()
		tk.Label(self, text="Password *").pack()
		password1_entry = tk.Entry(self, textvariable=password1, show="*", width=30)
		password1_entry.pack()
		tk.Label(self, text="Check Password *").pack()
		password2_entry = tk.Entry(self, textvariable=password2, show="*", width=30)
		password2_entry.pack()
		tk.Label(self, text="").pack()
		tk.Button(self, text="Register", width=10, height=1, bg="green",
					command=lambda: controller.register_user(username_entry, password1_entry, password2_entry, email_entry,
															username, password1, password2, email)).pack()

		button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))

		button1.pack(pady=10)


class StartPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		register_label = tk.Label(self, text="If not registered: ", font=30)
		register_label.pack(padx=10, pady=30)
		register_page = tk.Button(self, text="Register", width=10, height=1, bg="green",
				  command=lambda: controller.show_frame(PageRegister))
		register_page.pack()
		login_label = tk.Label(self, text="If you have an account: ", font=30)
		login_label.pack(padx=10, pady=30)
		login_page = tk.Button(self, text="Login", width=10, height=1, bg="cyan",
							   command=lambda: controller.show_frame(LoginPage))
		login_page.pack()


class MainPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		title1 = tk.Label(self, text="Welcome to CS Revise!", font=30)
		title1.pack(padx=10, pady=30)
		title2 = tk.Label(self, text="please, pick a course!", font=30)
		title2.pack(padx=10, pady=30)
		course1 = tk.Button(self, text="A-level", command=lambda: controller.show_frame(Alevel))
		course1.pack(padx=10, pady=30)
		course2 = tk.Button(self, text="GCSE", command=lambda: controller.show_frame(Gcse))
		course2.pack(padx=10, pady=30)


class Alevel(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		title = tk.Label(self, text="Choose the topic:", font=70)
		title.pack(padx=10, pady=50)
		alevel_computer_system_button = tk.Button(self, text="Computer Systems", font=40, command=lambda: controller.show_frame(Cs))
		alevel_computer_system_button.pack(padx=10, pady=30)
		alevel_algorithm_button = tk.Button(self, text="Algorithms and programming", font=40, command=lambda: controller.show_frame(Algorithms))
		alevel_algorithm_button.pack(padx=10, pady=30)
		back_to_courses = tk.Button(self, text="Back to courses!", font=30, command=lambda: controller.show_frame(MainPage))
		back_to_courses.pack(padx=10, pady=30)


class Gcse(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		now = tk.Label(self, text="Work In Progress!", font=30)
		now.pack(padx=10, pady=30)
		back_to_courses = tk.Button(self, text="Back to courses!", font=30,
									command=lambda: controller.show_frame(MainPage))
		back_to_courses.pack(padx=10, pady=30)


class Cs(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		characteristics_of_contemporary_processors = tk.Button(self, text="Characteristics of\n contemporary processors",
															   bg='#CCE5FF', font=30, command=lambda: controller.show_frame(cs1))
		characteristics_of_contemporary_processors.pack(padx=10, pady=30)
		software_and_development = tk.Button(self, text="Software and\n software development", bg="#CCE5FF", font=30, width=22)
		software_and_development.pack(padx=10, pady=30)
		exchanging_data = tk.Button(self, text="Exchanging data", font=30, width=22, bg='#CCE5FF')
		exchanging_data.pack(padx=10, pady=30)
		data_types = tk.Button(self, text="Data types", font=30, width=22, bg='#CCE5FF')
		data_types.pack(padx=10, pady=30)
		issues = tk.Button(self, text="Characteristics of\n contemporary processors", font=30, width=22, bg='#CCE5FF')
		issues.pack(padx=10, pady=30)
		back = tk.Button(self, text="Go back", font=30, width=14, bg='#99CCFF', height=10,
						 command=lambda: controller.show_frame(Alevel))
		back.pack(padx=10, pady=20)


class Algorithms(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		elements_of_computational_thinking = tk.Button(self, text="elements of\n computational thinking",
															   bg='#CCE5FF', font=30, width=22)
		elements_of_computational_thinking.pack(padx=10, pady=30)
		problem_solving = tk.Button(self, text="problem solving\n and programming",
													   bg='#CCE5FF', font=30, width=22)
		problem_solving.pack(padx=10, pady=30)
		Algorithms = tk.Button(self, text="Algorithms", bg='#CCE5FF', font=30, width=22)
		Algorithms.pack(padx=10, pady=30)
		back = tk.Button(self, text="Go back", font=30, width=14, bg='#99CCFF',
						 command=lambda: controller.show_frame(Alevel))
		back.pack(padx=10, pady=40)


class cs1(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		revise = tk.Button(self, text="revision", font=30, width=22, height=10, command=lambda: controller.show_frame(Revise1))
		revise.grid(row=0, column=0, pady=100)
		quiz = tk.Button(self, text="quiz", font=30, width=22, height=10, command=lambda: controller.show_frame(Quiz1))
		quiz.grid(row=0, column=1, padx=105, pady=100)


class Revise1(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		show_pdf = pdf.ShowPdf()
		pdf1 = show_pdf.pdf_view(self, pdf_location=r"pdfs/pd1.pdf", width=100, height=100)
		pdf1.pack()


class Quiz1(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)



app = GUI()
app.mainloop()
