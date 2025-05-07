from pathlib import Path
from ipywidgets import *
from IPython.display import clear_output
from IPython import display
import pandas as pd
import os


currentQuiz= None
txtprogrs = None

Qtitle = "Question 1:"
QText = "What is a correct syntax to output \"Hello World\" in Python?"
BOLD = '\033[1m'
RESET = '\033[0m'



def read_quizes():
    
    global Qzss

    qzlist = []

    rel_path = 'Quizzes'
    abs_file_path = os.path.join(Path.cwd(), rel_path)
    for root, dirs, files in os.walk(abs_file_path):
        for file in files:
            if (file.find('.csv')>-1):
                qzlist.append(file[:-4])
               
                
    Qzss.options = [x for x in Qzss.options]+qzlist
    
    return


class Question():
    def __init__(self, title, text,mchoice):
        self.title = title
        self.text = text
        self.type = mchoice
        self.choices = []
        self.correctchoice = None

    def getTitle(self):
        return self.title

    def getText(self):
        return self.text

    def getChoices(self):
        return self.choices

    def getCorrectChoice(self):
        return self.correctchoice

    def setChoices(self,myit):
        self.choices = myit
        return

    def IsMChoice(self):
        return self.type

class Quiz():
    def __init__(self, name):
        self.name = name
        self.questions = []
        self.currentQuestion = None

    def getName(self):
        return self.name

    def getQuestions(self):
        return self.questions

    def setCurrentQuestion(self,myqst):
        self.currentQuestion = myqst
        return

    def getCurrentQuestion(self):
        return self.currentQuestion
  


class VisualManager():
    def __init__(self):

        
        self.Qname= widgets.Label(value="Questions")
        self.Qqsts= widgets.Select(description="")
        self.Qqsts.layout.width ='95%'
        self.Qqsts.observe(self.open_question)
        self.description_out = widgets.Output()
        self.feedback_out = widgets.Output()
        self.qans_lbl= widgets.Label(value="Answer")
        self.qans_lbl.layout.visibility = 'hidden'
        self.qans_lbl.layout.display = 'none'
        self.writtenresp = widgets.Textarea(value='')
        self.writtenresp.layout.visibility = 'hidden'
        self.writtenresp.layout.display = 'none'
        self.choices = widgets.RadioButtons(options=[],description='',disabled=False)
        self.choices.layout.height = '150px'
        self.choices.layout.width = '99%'
        self.check = widgets.Button(description="Submit")
        self.check.on_click(self.check_selection)

        hboxleft = VBox(children=[self.Qname,self.Qqsts],layout=Layout(width = '15%'))
        qvbox = VBox(children=[self.description_out,self.qans_lbl,self.writtenresp,self.choices])

        hboxmiddle = VBox(children=[qvbox,HBox(children=[self.check],layout=Layout(align_items='stretch')),self.feedback_out],layout=Layout(width = '75%'))
        hboxright = HBox(children=[VBox(children=[])],layout=Layout(width = '15%'))

        self.QuizTab = HBox(children=[hboxleft,hboxmiddle,hboxright])



    def getQsts(self):
        return self.Qqsts

    def getQuizTab(self):
        return self.QuizTab

    ############################################################################################################################################
    def open_question(self,b):

        global currentQuiz,BOLD,RESET

        for qstn in currentQuiz.getQuestions():
            if qstn.getTitle() == self.Qqsts.value:
                currentQuiz.setCurrentQuestion(qstn)
                break

        if currentQuiz.getCurrentQuestion() is None:
           return
           
        try: 
            Qtitle = currentQuiz.getCurrentQuestion().getTitle()
            QText = currentQuiz.getCurrentQuestion().getText()
            with self.description_out:
                clear_output()
                print(f"""{BOLD}{Qtitle}{RESET}""")
                print("_______________________________")
                print(QText)
                print()
           
            if currentQuiz.getCurrentQuestion().IsMChoice():
    
                self.choices.layout.display = 'block'
                self.choices.layout.visibility = 'visible'
                
               
                self.qans_lbl.layout.visibility = 'hidden'
                self.qans_lbl.layout.display = 'none'
    
                self.writtenresp.layout.visibility = 'hidden'
                self.writtenresp.layout.display = 'none'
                
    
                chopts = []
            
                for choice in currentQuiz.getCurrentQuestion().getChoices():
                    chopts.append(choice[0])
                    
                self.choices.options = [x for x in chopts] 
            else:
                self.choices.layout.visibility = 'hidden'
                self.choices.layout.display = 'none'
                self.qans_lbl.layout.display = 'block'
                self.qans_lbl.layout.visibility = 'visible'
         
                self.writtenresp.layout.display = 'block'
                self.writtenresp.layout.visibility = 'visible'
         
            
            with self.feedback_out:
                clear_output()
                
        except Exception as e:  
            
            with self.feedback_out:
                clear_output()
                print('open quest error .. '+str(e))

        return
    ##############################################################################################################
    def check_selection(self,b):
        global currentQuiz
      
        correct_answers = []
    
        if not currentQuiz is None:
            for choice in currentQuiz.getCurrentQuestion().getChoices():
                if currentQuiz.getCurrentQuestion().IsMChoice():
                    if choice[1]:
                        correct_answers.append(choice[0])     
                else:
                    correct_answers = [choice[1]]
                    break
                    
        if currentQuiz.getCurrentQuestion().IsMChoice():
            a = str(self.choices.value)
            if a in correct_answers:
                s = '\x1b[6;30;42m' + "Correct." + '\x1b[0m' +"\n" #green color
            else:
                s = '\x1b[5;30;41m' + "Incorrect. " + '\x1b[0m' +"\n" #red color
        else:
            s = correct_answers[0]
            self.writtenresp.disabled = True
            
        with self.feedback_out:
            clear_output() 
            if not currentQuiz.getCurrentQuestion().IsMChoice():
                print('Correct Answer: ')
            else:
                s = 'Feedback: '+s
               
            print(s)
        return


def open_quiz(VisManager,DeelNo,tab_set):

    global currentQuiz

    qtslist = []

    quizstr = "Quiz Deel "+str(DeelNo)+"_Questions"
    qname = quizstr[:quizstr.find("_Questions")]

    tab_set.set_title(0,qname)

    currentQuiz = Quiz(qname)

    #rel_path = 'Quizzes'+'\\'+quizstr+'.csv'
    #abs_file_path = os.path.join(Path.cwd(), rel_path)

    url = ""
    if qname == "Quiz Deel 1":
        url = "https://github.com/muratfirat78/Python/raw/main/Quiz Deel 1_Questions.csv" 
    if qname == "Quiz Deel 2":
        url = "https://github.com/muratfirat78/Python/raw/main/Quiz Deel 2_Questions.csv" 

    url = url.replace(" ", "%20")
    Questions_df = pd.read_csv(url, sep=',') 
 
   
    for i,r in Questions_df.iterrows():
        newquestion = Question(r['Title'],r['Text'],r['Correctness'].find('~~')>-1)
        choices = r['Choices']
        correctness = r['Correctness']

        if newquestion.IsMChoice():

            while choices.find("~~") > -1:
               
                curr_choice = choices[:choices.find("~~")]
                my_correctness = correctness[:correctness.find("~~")]
    
        
                curr_correctness = False
                if my_correctness == 'True':
                    curr_correctness = True
                   
                newquestion.getChoices().append((curr_choice,curr_correctness))
                choices = choices[choices.find("~~")+2:]
                correctness = correctness[correctness.find("~~")+2:]
    
            curr_correctness = False
            if correctness == 'True':
                curr_correctness = True
            newquestion.getChoices().append((choices,curr_correctness))
            
        else:
            newquestion.getChoices().append((r['Choices'],r['Correctness']))
            
        currentQuiz.getQuestions().append(newquestion)
    
    VisManager.getQsts().options = [x.getTitle() for x in currentQuiz.getQuestions()]   

    
        
    return
##################################################################################################################################################
