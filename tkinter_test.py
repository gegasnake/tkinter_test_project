import hashlib
import sqlite3
import tkinter as tk
from tkPDFViewer import tkPDFViewer as pdf
from tkinter import *
from tkinter import messagebox as mb
import random
from tkinter import ttk
import json

LARGE_FONT = ("Verdana", 12)
connection_obj = sqlite3.connect('users.db')
cursor_obj = connection_obj.cursor()


class GUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)
        self.winfo_toplevel().title("CS Revise")
        self.winfo_toplevel().geometry("600x600")
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.user = ''
        self.score = [0]

        self.show_frame(StartPage)

    def show_frame(self, frame_class):

        frame = frame_class(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def log_out(self):
        self.user = ''
        self.score = [0]
        self.show_frame(StartPage)

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
                username_exists_message.pack(pady=100)
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
        query_to_receive_info_of_the_user = """SELECT Email, Password FROM USERS WHERE Email=? AND Password=?"""
        query_to_receive_username = """SELECT Username FROM USERS WHERE Email=? AND Password=?"""
        if cursor_obj.execute(query_to_receive_info_of_the_user, (email_info, hashed)).fetchone():

            self.user = cursor_obj.execute(query_to_receive_username, (email_info, hashed)).fetchone()
            # print(self.user)
            self.show_frame(MainPage)

        else:
            login_email_entry.delete(0, tk.END)
            login_password_entry.delete(0, tk.END)
            incorrect_credential_message = tk.Label(self, text="Incorrect credentials! Please check the information.",
                                                    fg="red")
            incorrect_credential_message.pack(pady=10)
            self.after(4000, lambda: incorrect_credential_message.destroy())

    def display_selected(self, choice):
        choice = choice
        print(choice)
        correct_query = """SELECT Correct FROM SCORES WHERE Username=? AND Quiz_ID=? ORDER BY Score_ID DESC LIMIT 1"""
        if cursor_obj.execute(correct_query, (self.user[0], int(choice[-1]))).fetchone():
            correct = cursor_obj.execute(correct_query, (self.user[0], int(choice[-1]))).fetchone()[0]
            wrong_query = """SELECT Wrong FROM SCORES WHERE Username=? AND Quiz_ID=? ORDER BY Score_ID  DESC LIMIT 1"""
            wrong = cursor_obj.execute(wrong_query, (self.user[0], int(choice[-1]))).fetchone()[0]
            score = int(correct / 10 * 100)
            result = f"Score: {score}%"
            mb.showinfo("Result", f"{result}\n{correct}\n{wrong}")
        else:
            mb.showinfo("Hello user!", "You haven't taken this Quiz yet.")

    def check_progress(self):
        progress = 0
        print(cursor_obj.execute("SELECT Correct FROM SCORES WHERE Username=?", (self.user[0],)).fetchall())
        for i in cursor_obj.execute("SELECT Correct FROM SCORES WHERE Username=?", (self.user[0],)).fetchall():
            if i[0] >= 8:
                progress += 1

        return progress / 8 * 100


class PDF(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.pdf_viewer = pdf.ShowPdf()

    def show_file(self, new_file):
        self.pdf_viewer.img_object_li = []
        self.pdf1 = None

        pdf1 = self.pdf_viewer.pdf_view(self, pdf_location=new_file, width=80, height=50)
        pdf1.pack(padx=10, pady=10)
        back_to_revise = tk.Button(self, text="back to revise", font=30, width=22, height=3,
                                   command=lambda: self.destroy())
        back_to_revise.pack(padx=10, pady=30)

        self.pdf1 = new_file

        print(self.pdf1)


class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        email_login = tk.StringVar()
        password_login = tk.StringVar()
        label1 = tk.Label(self, text="Please enter your details", font=50)
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

        button1 = tk.Button(self, text="Back to the main page", command=lambda: controller.show_frame(StartPage))

        button1.pack(pady=100)


class Quiz(tk.Toplevel):

    def __init__(self, quiz_title, user, data):

        self.quiz_title = quiz_title
        self.user = user
        self.data = data
        # keep a counter of correct answers
        self.correct = 0
        self.count = 0
        self.t = StringVar()
        with open(self.data) as f:
            info = json.load(f)

        temp = list(zip(info['questions'], info['answers'], info['options']))
        random.shuffle(temp)
        questions, answers, options = zip(*temp)
        self.questions = questions[:10]
        self.answers = answers[:10]
        self.options = options[:10]
        # no of questions
        self.data_size = len(self.questions)

        # dictionary of questions which were answered incorrectly
        self.wrong_answered_questions = {
            "questions": [],
            "answers": [],
            "options": []
        }

        get_quiz_id = """SELECT Quiz_ID FROM QUIZES WHERE Jason_file=?"""
        self.quiz_id = cursor_obj.execute(get_quiz_id, (self.data,)).fetchone()[0]
        # set question number to 0
        self.q_no = 0
        # opt_selected holds an integer value which is used for
        # selected option in a question.
        self.opt_selected = IntVar()

        super().__init__()

    def run(self):
        self.title(self.quiz_title)
        self.geometry("900x700")

        # assigns ques to the display_question function to update later.
        self.display_title()
        self.display_question()

        # displaying radio button for the current question and used to
        # display options for the current question
        self.opts = self.radio_buttons()

        # display options for the current question
        self.display_options()

        # displays the button for next and exit.
        self.buttons()

        self.t.set("00:00:00")
        lb = Label(self, textvariable=self.t, font="Times 28 bold", bg="white")
        lb.place(x=130, y=45)
        self.timer()

        self.mainloop()

    def timer(self):

        if self.count == 0:
            d = str(self.t.get())
            h, m, s = map(int, d.split(":"))
            h = int(h)
            m = int(m)
            s = int(s)
            if s < 59:
                s += 1
            elif s == 59:
                s = 0
                if m < 59:
                    m += 1
                elif m == 59:
                    m = 0
                    h += 1
            if h < 10:
                h = str(0) + str(h)
            else:
                h = str(h)
            if m < 10:
                m = str(0) + str(m)
            else:
                m = str(m)
            if s < 10:
                s = str(0) + str(s)
            else:
                s = str(s)
            d = h + ":" + m + ":" + s
            self.t.set(d)
            if self.count == 0:
                self.after(1000, self.timer)

    # This method shows the radio buttons to select the Question
    # on the screen at the specified position. It also returns a
    # list of radio button which are later used to add the options to
    # them.
    def radio_buttons(self):
        # initialize the list with an empty list of options
        q_list = []

        # position of the first option
        y_pos = 150

        # adding the options to the list
        while len(q_list) < 4:
            # setting the radio button properties
            radio_btn = Radiobutton(self, text=" ", variable=self.opt_selected, value=len(q_list) + 1,
                                    font=("ariel", 14),
                                    command=lambda: print(self.opt_selected.get()))

            # adding the button to the list
            q_list.append(radio_btn)

            # placing the button
            radio_btn.place(x=100, y=y_pos)

            # incrementing the y-axis position by 40
            y_pos += 40

        # return the radio buttons
        return q_list

    # This method is used to Display Title
    def display_title(self):
        # The title to be shown
        title = Label(self, text="computer science quiz",
                      width=50, bg="green", fg="white", font=("ariel", 20, "bold"))

        # place of the title
        title.place(x=0, y=2)

    def display_question(self):
        question = "Q" + str(self.q_no + 1) + "." + self.questions[self.q_no]
        # setting the Question properties
        q_no = Label(self, text=question, width=60, font=('ariel', 16, 'bold'), anchor='w')

        # placing the option on the screen
        q_no.place(x=70, y=100)

    def display_options(self):
        val = 0

        # deselecting the options
        self.opt_selected.set(0)

        # looping over the options to be displayed for the
        # text of the radio buttons.
        for option in self.options[self.q_no]:
            self.opts[val]['text'] = option
            val += 1

    def buttons(self):

        # The first button is the Next button to move to the
        # next Question
        next_button = Button(self, text="Next", command=lambda: self.next_btn(),
                             width=10, bg="blue", fg="white", font=("ariel", 16, "bold"))

        # placing the button  on the screen
        next_button.place(x=350, y=380)

        # This is the second button which is used to Quit the GUI
        quit_button = Button(self, text="Quit", command=self.destroy, width=5, bg="black", fg="white",
                             font=("ariel", 16, " bold"))

        # placing the Quit button on the screen
        quit_button.place(x=700, y=50)

    def next_btn(self):

        # Check if the answer is correct
        if self.check_ans():
            # if the answer is correct it increments the correct by 1
            self.correct += 1
        else:
            self.wrong_answered_questions["questions"].append(self.questions[self.q_no])
            self.wrong_answered_questions["answers"].append(self.answers[self.q_no])
            self.wrong_answered_questions["options"].append(self.options[self.q_no])
            print(self.wrong_answered_questions)

        # Moves to next Question by incrementing the q_no counter
        self.q_no += 1
        # checks if the q_no size is equal to the data size
        if self.q_no == self.data_size:

            # if it is correct then it displays the score
            self.display_result(self.quiz_id)

            # destroys the GUI
            self.destroy()
        else:
            # shows the next question
            self.display_question()
            self.display_options()

    def check_ans(self):

        # checks for if the selected option is correct
        if self.opt_selected.get() == self.answers[self.q_no]:
            # if the option is correct it returns true
            return True

    def display_result(self, quiz_id):
        # calculates the wrong count
        wrong_count = self.data_size - self.correct
        correct = f"Correct: {self.correct}"
        wrong = f"Wrong: {wrong_count}"

        # calculates the percentage of correct answers
        score = int(self.correct / self.data_size * 100)
        result = f"Score: {score}%"

        if cursor_obj.execute('''SELECT * FROM SCORES WHERE Quiz_ID=? AND Username=?''',
                              (quiz_id, self.user)).fetchone():
            cursor_obj.execute('''UPDATE SCORES SET Correct=?, Wrong=? WHERE Username=?''',
                               (self.correct, wrong_count, self.user,))
            connection_obj.commit()
        else:

            cursor_obj.execute(''' INSERT INTO SCORES(Username, Correct, Wrong, Quiz_ID) VALUES(?,?,?,?) ''', (
                self.user,
                self.correct,
                wrong_count,
                quiz_id,
            ))
            connection_obj.commit()

        print(self.wrong_answered_questions)
        mb.showinfo("Result", f"{result}\n{correct}\n{wrong}")


class PageRegister(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.winfo_toplevel().geometry("600x600")
        username = tk.StringVar()
        password1 = tk.StringVar()
        password2 = tk.StringVar()
        email = tk.StringVar()

        tk.Label(self, text="Please enter your details below to register:", font=30).pack(padx=10, pady=20)
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
                  command=lambda: controller.register_user(username_entry, password1_entry, password2_entry,
                                                           email_entry,
                                                           username, password1, password2, email)).pack()

        button1 = tk.Button(self, text="Back to the main page", command=lambda: controller.show_frame(StartPage))

        button1.pack(pady=10)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        welcome = tk.Label(self, text="CS revise is a subject revision platform offering revision "
                                      "\n materials and quizzes for effective exam preparation. "
                                      "\n\n Join our team now and enjoy our well-tested courses!", font=30)
        welcome.pack(padx=10, pady=30)
        register_label = tk.Label(self, text="Create an account here:", font=30)
        register_label.pack(padx=10, pady=30)
        register_page = tk.Button(self, text="Register", width=10, height=1, bg="green",
                                  command=lambda: controller.show_frame(PageRegister))
        register_page.pack()
        login_label = tk.Label(self, text="Already a member? ", font=30)
        login_label.pack(padx=10, pady=30)
        login_page = tk.Button(self, text="Login", width=10, height=1, bg="cyan",
                               command=lambda: controller.show_frame(LoginPage))
        login_page.pack()


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        my_profile = tk.Label(self, text="Profile: ", font=30)
        my_profile.place(x=10, y=10)
        profile_button = tk.Button(self, text="Your Profile", command=lambda: controller.show_frame(Profile))
        profile_button.place(x=80, y=5)
        title1 = tk.Label(self, text="Welcome to CS Revise " + controller.user[0] + "!", font=30)
        title1.pack(padx=10, pady=50)
        title2 = tk.Label(self, text="Pick your desired course.", font=30)
        title2.pack(padx=10, pady=30)
        course1 = tk.Button(self, text="A-level", command=lambda: controller.show_frame(Alevel))
        course1.pack(padx=10, pady=30)
        course2 = tk.Button(self, text="GCSE", command=lambda: controller.show_frame(Gcse))
        course2.pack(padx=10, pady=30)
        log_out_from_account = tk.Button(self, text="Log out", bg="red", command=lambda: controller.log_out())
        log_out_from_account.pack(padx=10, pady=30)


class Profile(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        name = tk.Label(self, text="Name:   " + controller.user[0], font=30)
        name.pack(padx=10, pady=30)
        query_to_receive_email = """SELECT Email FROM USERS WHERE Username=?"""
        receive_email = cursor_obj.execute(query_to_receive_email, (controller.user[0],)).fetchone()[0]
        email = tk.Label(self, text="Email:    " + receive_email, font=30)
        email.pack(padx=10, pady=30)
        variable = StringVar()
        variable.set("Quizes")  # default value

        w = OptionMenu(self, variable, "Quiz1", "Quiz2", "Quiz3",
                       command=lambda choice: controller.display_selected(variable.get()))
        w.pack()

        # Create progress bar
        progress_num = controller.check_progress()
        progress_label = tk.Label(self, text="Progress:")
        progress_label.pack(padx=10, pady=20)
        progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=300, value=progress_num)
        progress_bar.pack(padx=10, pady=10)

        # rehearse_quiz_variable = StringVar()
        # rehearse_quiz_variable.set("Rehearse Quizes")

        # rehearse the quiz by doing the wrong questions
        # w2 = OptionMenu(self, rehearse_quiz_variable, "rehearse_Quiz1", "rehearse_Quiz2", "rehearse_Quiz3",
        #               command=lambda choice: Quiz(rehearse_quiz_variable.get(), controller.user[0],
        #                                           "rehearse_quizes/" + rehearse_quiz_variable.get() + ".json").run())
        # w2.pack()

        back_to_main = tk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame(MainPage))
        back_to_main.pack(padx=10, pady=40)


class Gcse(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        now = tk.Label(self, text="Work In Progress! \n \n This course is currently under development. "
                                  "Please check back later.", font=30)
        now.pack(padx=10, pady=30)
        back_to_courses = tk.Button(self, text="Back to courses!", font=30,
                                    command=lambda: controller.show_frame(MainPage))
        back_to_courses.pack(padx=10, pady=30)


class Alevel(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        title = tk.Label(self, text="Choose a topic:", font=70)
        title.pack(padx=10, pady=50)
        alevel_computer_system_button = tk.Button(self, text="Computer Systems", font=40,
                                                  command=lambda: controller.show_frame(ComputerScience))
        alevel_computer_system_button.pack(padx=10, pady=30)
        alevel_algorithm_button = tk.Button(self, text="Algorithms and programming", font=40,
                                            command=lambda: controller.show_frame(Algorithms))
        alevel_algorithm_button.pack(padx=10, pady=30)
        back_to_courses = tk.Button(self, text="Back to courses!", font=30,
                                    command=lambda: controller.show_frame(MainPage))
        back_to_courses.pack(padx=10, pady=30)


class ComputerScience(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        characteristics_of_contemporary_processors = tk.Button(self,
                                                               text="Characteristics of\n contemporary processors",
                                                               bg='#CCE5FF', font=30,
                                                               command=lambda:
                                                               controller.show_frame(CharacteristicsOfContemporaryProcessors))
        characteristics_of_contemporary_processors.pack(padx=10, pady=30)
        software_and_development = tk.Button(self, text="Software and\n software development",
                                             bg="#CCE5FF", font=30, width=22,
                                             command=lambda: controller.show_frame(SoftwareAndSoftwareDevelopment))
        software_and_development.pack(padx=10, pady=30)
        exchanging_data = tk.Button(self, text="Exchanging data", font=30, width=22, bg='#CCE5FF',
                                    command=lambda: controller.show_frame(ExchangingData))
        exchanging_data.pack(padx=10, pady=30)
        data_types = tk.Button(self, text="Data types", font=30, width=22, bg='#CCE5FF',
                               command=lambda: controller.show_frame(DataTypes))
        data_types.pack(padx=10, pady=30)
        issues = tk.Button(self, text="Legal, Moral, Cultural\n and Ethical Issues", font=30, width=22, bg='#CCE5FF',
                           command=lambda: controller.show_frame(Issues))
        issues.pack(padx=10, pady=30)
        back = tk.Button(self, text="Go back", font=30, width=14, bg='#99CCFF', height=10,
                         command=lambda: controller.show_frame(Alevel))
        back.pack(padx=10, pady=20)


# *********************************************************************
class CharacteristicsOfContemporaryProcessors(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        revise = tk.Button(self, text="revision", font=30, width=22, height=10,
                           command=lambda: controller.show_frame(ReviseCharacteristicsOfContemporaryProcessors))
        revise.grid(row=0, column=0, pady=100)
        quiz = tk.Button(self, text="quiz", font=30, width=22, height=10,
                         command=lambda: Quiz("Quiz1", controller.user[0], 'quizes/Quiz1.json').run())
        quiz.grid(row=0, column=1, padx=105, pady=100)

        back_to_cs = tk.Button(self, text="Back to cs", font=30, width=22, height=10,
                               command=lambda: controller.show_frame(ComputerScience))
        back_to_cs.place(x=150, y=370)


class ReviseCharacteristicsOfContemporaryProcessors(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        structure_and_function_of_the_processor = tk.Button(self, text="Structure and function\n of the processor",
                                                            font=30, width=22, height=3,
                                                            command=lambda: PDF().show_file(r"pdfs/CharacteristicsOfContemporaryProcessors/structure_and_function_of_the_processor.pdf"))
        structure_and_function_of_the_processor.pack(padx=10, pady=30)
        types_of_processor = tk.Button(self, text="Types of Processor", font=30, width=22, height=3,
                                       command=lambda: PDF().show_file(r"pdfs/CharacteristicsOfContemporaryProcessors/types_of_processor.pdf"))
        types_of_processor.pack(padx=10, pady=30)
        input_output_storage = tk.Button(self, text="Input, Output and Storage",
                                         font=30, width=22, height=3,
                                         command=lambda: PDF().show_file(r"pdfs/CharacteristicsOfContemporaryProcessors/input_output_storage.pdf"))
        input_output_storage.pack(padx=10, pady=30)

        back_to_revise = tk.Button(self, text="Back to revision and quiz",
                                         font=30, width=20, height=2,
                                         command=lambda: controller.show_frame(CharacteristicsOfContemporaryProcessors))
        back_to_revise.pack(padx=10, pady=30)


# ****************************************************************************

class SoftwareAndSoftwareDevelopment(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        revise = tk.Button(self, text="revision", font=30, width=22, height=10,
                            command=lambda: controller.show_frame(ReviseSoftwareAndSoftwareDevelopment))
        revise.grid(row=0, column=0, pady=100)
        quiz = tk.Button(self, text="quiz", font=30, width=22, height=10,
                            command=lambda: Quiz("Quiz2", controller.user[0], 'quizes/Quiz2.json').run())
        quiz.grid(row=0, column=1, padx=105, pady=100)

        back_to_cs = tk.Button(self, text="Back to cs", font=30, width=22, height=10,
                                command=lambda: controller.show_frame(ComputerScience))
        back_to_cs.place(x=150, y=370)


class ReviseSoftwareAndSoftwareDevelopment(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        systems_software = tk.Button(self, text="Systems software",
                                     font=30, width=22, height=3,
                                     command=lambda: PDF().show_file(r"pdfs/SoftwareAndSoftwareDevelopment/systems_software.pdf"))
        systems_software.pack(padx=10, pady=30)
        applications_generation = tk.Button(self, text="Applications generation", font=30, width=22, height=3,
                                            command=lambda: PDF(
                                               ).show_file( r"pdfs/SoftwareAndSoftwareDevelopment/applications_generation.pdf"))
        applications_generation.pack(padx=10, pady=30)
        software_development = tk.Button(self, text="Software development",
                                                font=30, width=22, height=3,
                                                command=lambda: PDF(
                                                    ).show_file(r"pdfs/SoftwareAndSoftwareDevelopment/software_development.pdf"))
        software_development.pack(padx=10, pady=30)
        types_of_programming_languages = tk.Button(self, text="Types of programming languages",
                                         font=30, width=22, height=3,
                                         command=lambda: PDF(
                                         ).show_file(r"pdfs/SoftwareAndSoftwareDevelopment/types_of_programming_languages.pdf"))
        types_of_programming_languages.pack(padx=10, pady=30)

        back_to_revise = tk.Button(self, text="Back to revision and quiz",
                                         font=30, width=20, height=2,
                                         command=lambda: controller.show_frame(SoftwareAndSoftwareDevelopment))
        back_to_revise.pack(padx=10, pady=30)

# *************************************************************************************


class ExchangingData(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        revise = tk.Button(self, text="revision", font=30, width=22, height=10,
                            command=lambda: controller.show_frame(ReviseExchangingData))
        revise.grid(row=0, column=0, pady=100)
        quiz = tk.Button(self, text="quiz", font=30, width=22, height=10,
                            command=lambda: Quiz("Quiz3", controller.user[0], 'quizes/Quiz3.json').run())
        quiz.grid(row=0, column=1, padx=105, pady=100)

        back_to_cs = tk.Button(self, text="Back to cs", font=30, width=22, height=10,
                                command=lambda: controller.show_frame(ComputerScience))
        back_to_cs.place(x=150, y=370)


class ReviseExchangingData(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        compression_encryption_hashing = tk.Button(self, text="Compression Encryption Hashing", font=30, width=22, height=3, command=lambda: PDF(
        ).show_file(r"pdfs/ExchangingData/compression_encryption_hashing.pdf"))
        compression_encryption_hashing.pack(padx=10, pady=30)
        databases = tk.Button(self, text="Databases", font=30, width=22, height=3, command=lambda: PDF(
            ).show_file(r"pdfs/ExchangingData/databases.pdf"))
        databases.pack(padx=10, pady=30)
        networks = tk.Button(self, text="Networks", font=30, width=22, height=3,
                            command=lambda: PDF().show_file(r"pdfs/ExchangingData/networks.pdf"))
        networks.pack(padx=10, pady=30)
        web_technologies = tk.Button(self, text="Web technologies",
                                     font=30, width=22, height=3,
                                     command=lambda: PDF().show_file( r"pdfs/ExchangingData/web_technologies.pdf"))
        web_technologies.pack(padx=10, pady=30)

        back_to_revise = tk.Button(self, text="Back to revision and quiz",
                                         font=30, width=20, height=2,
                                         command=lambda: controller.show_frame(ExchangingData))
        back_to_revise.pack(padx=10, pady=30)

# ***************************************************************************************


class DataTypes(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        revise = tk.Button(self, text="revision", font=30, width=22, height=10,
                            command=lambda: controller.show_frame(ReviseDataTypes))
        revise.grid(row=0, column=0, pady=100)
        quiz = tk.Button(self, text="quiz", font=30, width=22, height=10,
                            command=lambda: Quiz("Quiz4", controller.user[0], 'quizes/Quiz4.json').run())
        quiz.grid(row=0, column=1, padx=105, pady=100)

        back_to_cs = tk.Button(self, text="Back to cs", font=30, width=22, height=10,
                                command=lambda: controller.show_frame(ComputerScience))
        back_to_cs.place(x=150, y=370)


class ReviseDataTypes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        data_types = tk.Button(self, text="Data types", font=30, width=22, height=3, command=lambda: PDF(
            ).show_file(r"pdfs/DataTypes/data_types.pdf"))
        data_types.pack(padx=10, pady=30)
        data_structures = tk.Button(self, text="Data structures", font=30, width=22, height=3,
                                    command=lambda: PDF(
                                        ).show_file(r"pdfs/DataTypes/data_structures.pdf"))
        data_structures.pack(padx=10, pady=30)
        boolean_algebra = tk.Button(self, text="Boolean algebra",
                                    font=30, width=22, height=3,
                                    command=lambda: PDF(
                                       ).show_file( r"pdfs/DataTypes/boolean_algebra.pdf"))
        boolean_algebra.pack(padx=10, pady=30)

        back_to_revise = tk.Button(self, text="Back to revision and quiz",
                                         font=30, width=20, height=2,
                                         command=lambda: controller.show_frame(DataTypes))
        back_to_revise.pack(padx=10, pady=30)

# ***************************************************************************************


class Issues(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        revise = tk.Button(self, text="revision", font=30, width=22, height=10,
                           command=lambda: controller.show_frame(ReviseDataTypes))
        revise.grid(row=0, column=0, pady=100)
        quiz = tk.Button(self, text="quiz", font=30, width=22, height=10,
                         command=lambda: Quiz("Quiz5", controller.user[0], 'quizes/Quiz5.json').run())
        quiz.grid(row=0, column=1, padx=105, pady=100)

        back_to_cs = tk.Button(self, text="Back to cs", font=30, width=22, height=10,
                               command=lambda: controller.show_frame(ComputerScience))
        back_to_cs.place(x=150, y=370)


class ReviseIssues(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        computing_related_legislation = tk.Button(self, text="Computing related legislation",
                                                  font=30, width=22, height=3,
                                                  command=lambda: PDF(
                                                      ).show_file(r"pdfs/Issues/computing_related_legislation.pdf"))
        computing_related_legislation.pack(padx=10, pady=30)
        moral_and_ethical_issues = tk.Button(self, text="Moral and Ethical Issues", font=30, width=22, height=3,
                                             command=lambda: PDF(
                                                 ).show_file(r"pdfs/Issues/moral_and_ethical_issues.pdf"))
        moral_and_ethical_issues.pack(padx=10, pady=30)

        back_to_revise = tk.Button(self, text="Back to revision and quiz",
                                         font=30, width=20, height=2,
                                         command=lambda: controller.show_frame(Issues))
        back_to_revise.pack(padx=10, pady=30)


class Algorithms(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        elements_of_computational_thinking = tk.Button(self, text="elements of\n computational thinking",
                                                       bg='#CCE5FF', font=30, width=22, command=lambda: controller.show_frame(ElementsOfComputationalThinking))
        elements_of_computational_thinking.pack(padx=10, pady=30)
        problem_solving = tk.Button(self, text="problem solving\n and programming",
                                    bg='#CCE5FF', font=30, width=22, command=lambda: controller.show_frame(ProblemSolvingAndProgramming))
        problem_solving.pack(padx=10, pady=30)
        algorithms = tk.Button(self, text="Algorithms", bg='#CCE5FF', font=30, width=22, command=lambda: controller.show_frame(SubAlgorithms))
        algorithms.pack(padx=10, pady=30)
        back = tk.Button(self, text="Go back", font=30, width=14, bg='#99CCFF',
                         command=lambda: controller.show_frame(Alevel))
        back.pack(padx=10, pady=40)


class ElementsOfComputationalThinking(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        revise = tk.Button(self, text="revision", font=30, width=22, height=10,
                           command=lambda: controller.show_frame(ReviseElementsOfComputationalThinking))
        revise.grid(row=0, column=0, pady=100)
        quiz = tk.Button(self, text="quiz", font=30, width=22, height=10,
                         command=lambda: Quiz("Quiz6", controller.user[0], 'quizes/Quiz6.json').run())
        quiz.grid(row=0, column=1, padx=105, pady=100)

        back_to_cs = tk.Button(self, text="Back to cs", font=30, width=22, height=10,
                               command=lambda: controller.show_frame(Algorithms))
        back_to_cs.place(x=150, y=370)


class ReviseElementsOfComputationalThinking(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        thinking_abstractly = tk.Button(self, text="Thinking abstractly", font=30, width=22, height=1, command=lambda: PDF(
        ).show_file(r"pdfs/ElementsOfComputationalThinking/thinking_abstractly.pdf"))
        thinking_abstractly.pack(padx=10, pady=30)
        thinking_ahead = tk.Button(self, text="Thinking ahead", font=30, width=22, height=1,
                                    command=lambda: PDF(
                                    ).show_file(r"pdfs/ElementsOfComputationalThinking/thinking_ahead.pdf"))
        thinking_ahead.pack(padx=10, pady=30)
        thinking_procedurally = tk.Button(self, text="Thinking procedurally",
                                    font=30, width=22, height=1,
                                    command=lambda: PDF(
                                    ).show_file(r"pdfs/ElementsOfComputationalThinking/thinking_procedurally.pdf"))
        thinking_procedurally.pack(padx=10, pady=30)
        thinking_logically = tk.Button(self, text="Thinking logically",
                                          font=30, width=22, height=1,
                                          command=lambda: PDF(
                                          ).show_file(r"pdfs/ElementsOfComputationalThinking/thinking_logically.pdf"))
        thinking_logically.pack(padx=10, pady=30)
        thinking_concurrently = tk.Button(self, text="Thinking concurrently",
                                          font=30, width=22, height=1,
                                          command=lambda: PDF(
                                          ).show_file(r"pdfs/ElementsOfComputationalThinking/thinking_concurrently.pdf"))
        thinking_concurrently.pack(padx=10, pady=30)

        back_to_revise = tk.Button(self, text="Back to revision and quiz",
                                   font=30, width=20, height=2,
                                   command=lambda: controller.show_frame(ElementsOfComputationalThinking))
        back_to_revise.pack(padx=10, pady=30)


class ProblemSolvingAndProgramming(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        revise = tk.Button(self, text="revision", font=30, width=22, height=10,
                           command=lambda: controller.show_frame(ReviseProblemSolvingAndProgramming))
        revise.grid(row=0, column=0, pady=100)
        quiz = tk.Button(self, text="quiz", font=30, width=22, height=10,
                         command=lambda: Quiz("Quiz7", controller.user[0], 'quizes/Quiz7.json').run())
        quiz.grid(row=0, column=1, padx=105, pady=100)

        back_to_cs = tk.Button(self, text="Back to cs", font=30, width=22, height=10,
                               command=lambda: controller.show_frame(Algorithms))
        back_to_cs.place(x=150, y=370)


class ReviseProblemSolvingAndProgramming(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        programming_techniques = tk.Button(self, text="Programming techniques", font=30, width=22, height=3, command=lambda: PDF(
        ).show_file(r"pdfs/ProblemSolvingAndProgramming/programming_techniques.pdf"))
        programming_techniques.pack(padx=10, pady=30)
        computational_methods = tk.Button(self, text="Computational methods", font=30, width=22, height=3,
                                    command=lambda: PDF(
                                    ).show_file(r"pdfs/ProblemSolvingAndProgramming/computational_methods.pdf"))
        computational_methods.pack(padx=10, pady=30)

        back_to_revise = tk.Button(self, text="Back to revision and quiz",
                                   font=30, width=20, height=2,
                                   command=lambda: controller.show_frame(ProblemSolvingAndProgramming))
        back_to_revise.pack(padx=10, pady=30)


class SubAlgorithms(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        revise = tk.Button(self, text="revision", font=30, width=22, height=10,
                           command=lambda: controller.show_frame(ReviseSubAlgorithms))
        revise.grid(row=0, column=0, pady=100)
        quiz = tk.Button(self, text="quiz", font=30, width=22, height=10,
                         command=lambda: Quiz("Quiz8", controller.user[0], 'quizes/Quiz8.json').run())
        quiz.grid(row=0, column=1, padx=105, pady=100)

        back_to_cs = tk.Button(self, text="Back to cs", font=30, width=22, height=10,
                               command=lambda: controller.show_frame(Algorithms))
        back_to_cs.place(x=150, y=370)


class ReviseSubAlgorithms(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        algorithms_for_the_main_data_structures = tk.Button(self, text="Algorithms for the\n main data structures", font=30, width=22, height=2, command=lambda: PDF(
        ).show_file(r"pdfs/SubAlgorithms/algorithms_for_the_main_data_structures.pdf"))
        algorithms_for_the_main_data_structures.pack(padx=10, pady=30)
        analysis_design_and_comparison_of_algorithms = tk.Button(self,
                                                                 text="Analysis design and\n comparison of algorithms",
                                                                 font=30, width=22, height=2,
                                    command=lambda: PDF(
                                    ).show_file(r"pdfs/SubAlgorithms/analysis_design_and_comparison_of_algorithms.pdf"))
        analysis_design_and_comparison_of_algorithms.pack(padx=10, pady=30)
        path_finding_algorithms = tk.Button(self, text="Path finding algorithms",
                                    font=30, width=22, height=1,
                                    command=lambda: PDF(
                                    ).show_file(r"pdfs/SubAlgorithms/path_finding_algorithms.pdf"))
        path_finding_algorithms.pack(padx=10, pady=30)
        searching_algorithms = tk.Button(self, text="Searching algorithms",
                                          font=30, width=22, height=1,
                                          command=lambda: PDF(
                                          ).show_file(r"pdfs/SubAlgorithms/searching_algorithms.pdf"))
        searching_algorithms.pack(padx=10, pady=30)
        sorting_algorithms = tk.Button(self, text="Sorting algorithms",
                                          font=30, width=22, height=1,
                                          command=lambda: PDF(
                                          ).show_file(r"pdfs/SubAlgorithms/sorting_algorithms.pdf"))
        sorting_algorithms.pack(padx=10, pady=30)

        back_to_revise = tk.Button(self, text="Back to revision and quiz",
                                   font=30, width=20, height=2,
                                   command=lambda: controller.show_frame(SubAlgorithms))
        back_to_revise.pack(padx=10, pady=30)


GUI().mainloop()
