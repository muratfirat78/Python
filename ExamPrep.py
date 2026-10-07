from pathlib import Path
from ipywidgets import *
from IPython.display import clear_output
from IPython import display
import pandas as pd
import os
from datetime import timedelta,date,datetime
import math


currentQuiz= None
QuestionTopics = dict() # key: topicname, val: [Questions]
txtprogrs = None
allQuestions = [] 

ExamMngr = None
VisualMngr = None

Qtitle = "Question 1:"
QText = "What is a correct syntax to output \"Hello World\" in Python?"
BOLD = '\033[1m'
RESET = '\033[0m'


class ExamManager():
    def __init__(self,coursecode,online):

        self.QuestionBank = QuestionBank(self)
        self.Online = online
        self.CourseCode = coursecode
        self.CurrentTeacher = None
        self.Exams = []
        self.CurrentExam = None

    def setCurrentExam(self,xm):
        self.CurrentExam = xm
        return 
    def getCurrentExam(self):
        return self.CurrentExam
   
    def getExams(self):
        return self.Exams

    def setCurrentTeacher(self,tch):
        self.CurrentTeacher = tch
        return

    def getCurrentTeacher(self):
        return self.CurrentTeacher 

    def getCourseCode(self):
        return self.CourseCode

    def isOnline(self):
        return self.Online

    def getQuestionBank(self):
        return self.QuestionBank

    def checkQBanks(self,progress):

        keyword = self.getCourseCode()+"_QBank_"+self.getCurrentTeacher()
        qbanksdetected = 0
        filename = None

        
        try: 
            if not self.isOnline(): 
                abs_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"questions")
                for root, dirs, files in os.walk(abs_file_path):
                    for name in files:
                        if name.find("checkpoint") > -1:
                            continue
                        if name.find(keyword) > -1:
                            filename = name
               
                            
            else:
                source_directory = '/content/'
                for myname in os.listdir(source_directory):
                    if myname.find(keyword) > -1:
                        qbanksdetected+=1
                        filename = myname

            questions_df = pd.DataFrame()
            if not self.isOnline(): 
                questions_df = pd.read_csv(abs_file_path+'/'+filename)
        
            else:
                    #print("filename: "+filename)
                progress.value+="Info: questions to check "+"\n"
                questions_df = pd.read_csv(source_directory+'/'+filename)
                progress.value+="Info: questions  "+str(len(questions_df))+"\n"

            for i,r in questions_df.iterrows():
                progress.value+="Info: question title "+str(r['Title'])+"\n"

                progress.value+="Info: "+str(r['Title'])+" -- "+str(i)+" -- "+str(r['Date'])+"\n"

                qstid = r['Title']+"_"+str(i)+"_"+str(r['Date'])
           
                myquest = Question(qstid,None,None,True,None)
                myquest.setTitle(r['Title']); myquest.setText(r['Text']);

                if pd.isna(r['Main_Topic']):
                    myquest.setMainTopic('De basis')
                else:
                    myquest.setMainTopic(r['Main_Topic'])
                if not pd.isna(r['Points']):
                    myquest.setPoints(r['Points'])
                myquest.setExplanation(r['Explanation']); myquest.setTeacher(r['Teacher']); myquest.setDate(r['Date'])
                str_choices = str(r['Choices']); str_correctness = str(r['Correctness'])
                if str_choices.find("~~") > -1:
                    choices = str_choices.split("~~")
                    correctness = str_correctness.split("~~")
        
                    for choiceid in range(len(choices)):
                        ch_correctness = True if correctness[choiceid] == "True" else False
                        myquest.getChoices().append((choices[choiceid],ch_correctness))
                            
                self.QuestionBank.getQuestions().append(myquest)
                
                
            
        except Exception as e:
            progress.value+="ERROR: in checking question banks "+str(e)+"\n"

        progress.value+="Info: question banks detected "+str(qbanksdetected)+"\n"
        #print("Info: quesntionbank has "+str(len(self.QuestionBank.getQuestions()))+" questions")  


        return 
    

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

class QuestionBank():
    def __init__(self,exmgr):
        self.Questions = []
        self.ExamManager = exmgr
        self.QuestionInPreparation = None

    def setQuestionInPrep(self,myqs):
        self.QuestionInPreparation = myqs
        return

    def getQuestionInPrep(self):
        return self.QuestionInPreparation 

    def getQuestions(self):
        return self.Questions

    def save_Questions(self,progress):

        question_df = pd.DataFrame(columns=["ID","Title","Text","Main_Topic","Points","Explanation","Teacher","Choices","Correctness","Date"])
      
        source_directory = '/content/'


        try: 
        
            for question in self.getQuestions():
                choices = "";correctness = ""
                for choice in question.getChoices():
                    choices+=("~~" if choices!= "" else "")+choice[0]
                    correctness+=("~~" if correctness!= "" else "")+str(choice[1])
                questrow = {"ID":question.getID(),"Title":question.getTitle(),"Text":question.getText(),"Main_Topic":question.getMainTopic(),
                            "Points":question.getPoints(),"Explanation":question.getExplanation(),"Teacher":question.getTeacher() if question.getTeacher()!=None else self.ExamManager.getCurrentTeacher() ,"Choices":choices,"Correctness":correctness,"Date":question.getDate()}
                question_df.loc[len(question_df)] = questrow
              
    
            if not self.ExamManager.isOnline():
                question_df.to_csv(os.path.join("questions",self.ExamManager.getCourseCode()+"_QBank_"+str(self.ExamManager.getCurrentTeacher())+".csv"),index = False)
            else:
                question_df.to_csv(source_directory+'/'+self.ExamManager.getCourseCode()+"_QBank_"+str(self.ExamManager.getCurrentTeacher())+".csv")
            return 
        except Exception as e:
            progress.value+="ERROR: in saving question banks "+str(e)+"\n"



    def writeQuestions(self):


        return 



class Exam():
    def __init__(self):
        self.Name = None
        self.Date = None
        self.TopicsDict = dict()
        self.Questions = []
        self.TotalPoints = None

    def getTopicsDict(self):
        return self.TopicsDict


    def setName(self,tr):
        self.Name =tr
        return

    def getName(self):
        return self.Name


    def setDate(self,tr):
        self.Date =tr
        return

    def getDate(self):
        return self.Date

    def getQuestions(self):
        return self.Questions

    def getTotalPoints(self):
        return self.TotalPoints

    def setTotalPoints(self,pts):
        self.TotalPoints = pts
        return 
            
            
    

class Question():
    def __init__(self,myid, title, text,mchoice,exp):
        self.title = title
        self.text = text
        self.type = mchoice
        self.choices = []
        self.correctchoice = None
        self.choicesdict = dict() #key: choice, val: True/False
        self.maintopic = None
        self.subtopic = None 
        self.explanation = exp
        self.date = None
        self.teacher = None
        self.date = None
        self.id = myid
        self.Points = None

    def setPoints(self,pts):
        self.Points = pts
        return
    def getPoints(self):
        return self.Points

    def getID(self):
        return self.id
    def setID(self,idtxt):
        self.id = idtxt
        return

    def setTeacher(self,tch):
        self.teacher = tch
        return

    def setDate(self,dt):
        self.date = dt
        return

    def getDate(self):
        return self.date

    def getTeacher(self):
        return self.teacher


    def setMainTopic(self,tp):
        self.maintopic = tp
        return

    def getMainTopic(self):
        return self.maintopic

    def setSubTopic(self,tp):
        self.subtopic = tp
        return

    def getSubTopic(self):
        return self.subtopic 

    def setExplanation(self,txt):
        self.explanation = txt
        return
    def getExplanation(self):
        return self.explanation 
    
    def setDate(self,dt):
        self.date = dt

    def getDate(self):
        return self.date 

    def setTitle(self,tt):
        self.title = tt
        return

    def getTitle(self):
        return self.title

    def getExplanation(self):
        return self.explanation

    def getText(self):
        return self.text
    def setText(self,txt):
        self.text = txt
        return 

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
        self.NewQuest= widgets.Button(description="New Question")
        self.EditQuest= widgets.Button(description="Edit Question")
        self.RemoveQuest= widgets.Button(description="Remove Question")
        self.NewQuestSave= widgets.Button(description="Save Question")
        self.Qqsts.layout.width ='95%'
        self.Qqsts.layout.height ='250px'
        self.Qqsts.observe(self.open_question)
        self.description_out = widgets.Output()
        self.feedback_out = widgets.Output()
        self.qans_lbl= widgets.Label(value="Answer")
        self.NewQDate= widgets.Label(value="Date: "+str((datetime.now().date())))
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
        self.MenuDict = dict() #key: menu name, val: [menu items]
        self.NewQuestionOutput = widgets.Output()
        self.NewQuest.on_click(self.startNewQeustion)
        self.EditQuest.on_click(self.editQuestion)
        self.Choice1 = widgets.Text(value='',description = 'Choice: ')
        self.Choice2 = widgets.Text(value='',description = 'Choice: ')
        self.Choice3 = widgets.Text(value='',description = 'Choice: ')
        self.Choice4 = widgets.Text(value='',description = 'Choice: ')
        self.Cbox1 = widgets.Checkbox(value=False,description='Correct',disabled=False)
        self.Cbox2 = widgets.Checkbox(value=False,description='Correct',disabled=False)
        self.Cbox3 = widgets.Checkbox(value=False,description='Correct',disabled=False)
        self.Cbox4 = widgets.Checkbox(value=False,description='Correct',disabled=False)
        self.ExamManager = None 

    
        color = "gray"; mytext ="Title:"
        self.NewQTNameTtl = widgets.HTML("")  
        self.NewQTNameTtl.value = f'<span style="color:{color};"><b>{mytext}</b></span>'

        self.Points = widgets.Dropdown(options = [2.5,5,7.5,10],description = 'Points: ')

        
        self.NewQName= widgets.Text(value='')
       

        self.teachers = widgets.RadioButtons(options=["Murat Firat","Hugo Jonker"],description='',disabled=False)
        self.teachers.observe(self.assignTeacher)

        color = "olive"; mytext ="Question Text"
        self.NewQTxtTtl = widgets.HTML("")  
        self.NewQTxtTtl.value = f'<span style="color:{color};"><b>{mytext}</b></span>'
        self.NewQTxt= widgets.Textarea(value='')


        color = "red"; mytext ="IB3502 Python Programming"
        self.CourseLbl = widgets.HTML("")  
        self.CourseLbl.value = f'<span style="color:{color};"><b>{mytext}</b></span>'

        self.Teacher_lbl= widgets.Label(value="Teacher: ")
        self.Points_lbl= widgets.Label(value="Points: ")


        self.exam_date= widgets.Label(value="Exam date: ")

        self.ExamName = widgets.Text(value='',description = 'Name: ')
        self.ExamDate = widgets.DatePicker(description='Exam Date',disabled=False)
         
      
   
        color = "olive"; mytext ="Explanation"
        self.NewQExpTtl = widgets.HTML("")  
        self.NewQExpTtl.value = f'<span style="color:{color};"><b>{mytext}</b></span>'
        
        self.NewQExp= widgets.Textarea(value='')
        self.NewQTopics = widgets.Dropdown(options = ["De basis","Data Typen","Control Flow","Functies en modules","Objectgeorienteerd Programmeren ","Regulair expressies"],description = 'Topic: ')
        self.NewQType = widgets.Dropdown(options = ["Two-choice","Three-choice","Four-choice"],description = 'Type: ')
        self.NewQType.observe(self.applyqtype)

        self.NewQuestSave.on_click(self.saveQuestion)
        self.RemoveQuest.on_click(self.removeQuestion)
       

        self.Progress= widgets.Textarea(value='',description ="Progress")
        self.Progress.layout.width = "600px"
        self.Progress.layout.height = "80px"

        self.choicebox1 = VBox(children=[HBox(children=[self.Choice1,self.Cbox1])])
        self.choicebox2 =  VBox(children=[HBox(children=[self.Choice2,self.Cbox2])])
        self.choicebox3 =  VBox(children=[HBox(children=[self.Choice3,self.Cbox3])])
        self.choicebox4 =  VBox(children=[HBox(children=[self.Choice4,self.Cbox4])])


        self.Tname= widgets.Label(value="Topics")
        self.Topics= widgets.Select(description="")

        self.Ename= widgets.Label(value="Exams")
        self.Examlist= widgets.Select(description="")
        self.Examlist.observe(self.showExam)
        
        self.Etopics= widgets.Label(value="Exam Topics")
        self.Examtopics= widgets.Select(description="")

        self.NewExam= widgets.Button(description="New Exam")
        self.QNewExam= widgets.Button(description="Quit")
        self.QNewExam.on_click(self.quitExam)
        self.NewExam.on_click(self.newExam)


        
        
        self.Exname= widgets.Label(value="Exam Questions")
        self.ExQqsts= widgets.Select(description="")

        self.ExamPoints = widgets.Dropdown(options = [200],description = 'Total Points: ')

        self.AddQuest= widgets.Button(description=">> Add Question >>")
        self.AddQuest.on_click(self.addQuestionExam)

        self.Topics.layout.width ='95%'
        self.Topics.layout.height ='100px'

        self.Topics.observe(self.findTopicQuestions)
        
      
        self.choicebxlist = [self.choicebox1,self.choicebox2,self.choicebox3,self.choicebox4]
        self.choicelist = [(self.Choice1,self.Cbox1),(self.Choice2,self.Cbox2),(self.Choice3,self.Cbox3),(self.Choice4,self.Cbox4)]

    def getTopics(self):
        return self.Topics
    def getEditQuestionButton(self):
        return self.EditQuest

    def assignTeacher(self,b):

        self.assignCurrentTeacher()
   
        return 


    def showExam(self,b):

        global ExamMngr 

        selectedexam = self.Examlist.value

        for exam in ExamMngr.getExams():
            if exam.getName() == selectedexam:
                ExamMngr.setCurrentExam(exam)
                break

        if ExamMngr.getCurrentExam()!= None:
            self.exam_date.value = str(ExamMngr.getCurrentExam().getDate())
            
                

        return 

    def quitExam(self,b):

        self.NewExamBox.layout.visibility = 'hidden' 
        self.NewExamBox.layout.display = 'none'
    
        self.ExamInfobox.layout.display = 'block'
        self.ExamInfobox.layout.visibility = 'visible' 
                
        self.ExamInfobox2.layout.display = 'block'
        self.ExamInfobox2.layout.visibility = 'visible' 

        self.QNewExam.layout.visibility = 'hidden' 
        self.QNewExam.layout.display = 'none'

        self.NewExam.description = "New Exam"


        return 

    def addQuestionExam(self,b):

        try: 

            sel_questionname = self.Qqsts.value
    
            for question in self.getExamManager().getQuestionBank().getQuestions():
                if question.getTitle() == sel_questionname:
                    if not question in self.getExamManager().getCurrentExam().getQuestions():
                        self.getExamManager().getCurrentExam().getQuestions().append(question)
                    break
                    
    
            self.ExQqsts.options = [q.getTitle() for q in self.getExamManager().getCurrentExam().getQuestions()]


        except Exception as e:             
            self.Progress.value +='ERROR: In adding question t exam .. '+str(e)+"\n"
                

        
        return


    def newExam(self,b):

        global ExamMngr 

        if  self.NewExam.description == "New Exam":

            self.NewExam.description = "Save Exam"
            self.ExamInfobox.layout.visibility = 'hidden' 
            self.ExamInfobox.layout.display = 'none'
            self.ExamInfobox2.layout.visibility = 'hidden' 
            self.ExamInfobox2.layout.display = 'none'
            
            self.NewExamBox.layout.display = 'block'
            self.NewExamBox.layout.visibility = 'visible'

            self.QNewExam.layout.display = 'block'
            self.QNewExam.layout.visibility = 'visible' 
            
            

        else:

            try: 
                newExam = Exam()
                newExam.setName(self.ExamName.value)
                newExam.setDate(self.ExamDate.value)
                newExam.setTotalPoints(self.ExamPoints.value)
    
                ExamMngr.getExams().append(newExam)
                
    
                self.Examlist.options = [e.getName() for e in ExamMngr.getExams()]
            
                
                self.NewExam.description = "New Exam"
    
                self.NewExamBox.layout.visibility = 'hidden' 
                self.NewExamBox.layout.display = 'none'
    
                self.ExamInfobox.layout.display = 'block'
                self.ExamInfobox.layout.visibility = 'visible' 
                
                self.ExamInfobox2.layout.display = 'block'
                self.ExamInfobox2.layout.visibility = 'visible' 

                self.QNewExam.layout.visibility = 'hidden' 
                self.QNewExam.layout.display = 'none'
                

                
            except Exception as e:             
                self.Progress.value +='ERROR: In saving exam .. '+str(e)+"\n"
                

        return

    def assignCurrentTeacher(self):

        global currentQuiz,QuestionTopics

        teacher = str(self.teachers.value)
         
        self.getExamManager().setCurrentTeacher(teacher)
        self.getExamManager().getQuestionBank().getQuestions().clear()
        currentQuiz.getQuestions().clear()


        self.Progress.value +='INFO: assigning teacher .. '+str(self.getExamManager().getCurrentTeacher())+"\n"

        

        try: 
            self.Progress.value+="INFO: before qbank check.. "+"\n"
            self.getExamManager().checkQBanks(self.Progress)
            self.Progress.value+="INFO: after qbank check.. "+str(len(self.getExamManager().getQuestionBank().getQuestions()))+"\n"
            if len(self.getExamManager().getQuestionBank().getQuestions()) > 0: 
                for question in self.getExamManager().getQuestionBank().getQuestions():
                    if not question.getMainTopic() in QuestionTopics:
                        QuestionTopics[question.getMainTopic()] = []
                    QuestionTopics[question.getMainTopic()].append(question)
                    
                    currentQuiz.getQuestions().append(question)
                self.getQsts().options = [x.getTitle() for x in currentQuiz.getQuestions()]  

                topcopts = ["All"]
                self.getTopics().options = topcopts+[x for x in QuestionTopics.keys()]  
                
        except Exception as e:             
            self.Progress.value +='ERROR: In assigning teacher .. '+str(e)+"\n"

        return
        



    def getChoiceList(self):
        return self.choicelist


    def getNewQExp(self):
        return self.NewQExp

    def setExamManager(self,mgr):
        self.ExamManager = mgr
        return

    def getExamManager(self):
        return self.ExamManager
   
    def getQsts(self):
        return self.Qqsts
    def getNewQTopicsMenu(self):
        return self.NewQTopics
    def getNewQTitle(self):
        return self.NewQName
    def getNewQText(self):
        return self.NewQTxt

    def getNewQuestButton(self):
        return self.NewQuest

    def getProgress(self):
        return self.Progress

    def saveQuestion(self,b):

        global currentQuiz

        try: 
            qstbank = self.getExamManager().getQuestionBank()

            

            qstbank.getQuestionInPrep().setTitle(self.getNewQTitle().value)
            qstbank.getQuestionInPrep().setMainTopic(self.getNewQTopicsMenu().value)
            qstbank.getQuestionInPrep().setText(self.getNewQText().value)
            qstbank.getQuestionInPrep().setTeacher(self.getExamManager().getCurrentTeacher())
            qstbank.getQuestionInPrep().setDate(datetime.now().date())
            qstbank.getQuestionInPrep().setExplanation(self.getNewQExp().value)
            qstbank.getQuestionInPrep().setPoints(self.Points.value)

            qstid = qstbank.getQuestionInPrep().getTitle()+"_"+str(len(qstbank.getQuestions()))+"_"+str((datetime.now().date()))

            qstbank.getQuestionInPrep().setID(qstid)

            qstbank.getQuestionInPrep().getChoices().clear()
            for choice in VisualMngr.getChoiceList():
                self.Progress.value +=" choice ..."+str(choice[0].value)+"\n"
                if choice[0].value != "":
                    qstbank.getQuestionInPrep().getChoices().append((choice[0].value,choice[1].value))                
        
            self.Progress.value +=" New question is ready to go! "+"\n"

            #if currentQuiz.getCurrentQuestion() != self.getExamManager().getQuestionBank().getQuestionInPrep():
            if not self.getExamManager().getQuestionBank().getQuestionInPrep() in currentQuiz.getQuestions():
                currentQuiz.getQuestions().append(self.getExamManager().getQuestionBank().getQuestionInPrep())
            if not self.getExamManager().getQuestionBank().getQuestionInPrep() in self.getExamManager().getQuestionBank().getQuestions():
                self.getExamManager().getQuestionBank().getQuestions().append(self.getExamManager().getQuestionBank().getQuestionInPrep())
            self.getExamManager().getQuestionBank().save_Questions(self.Progress)


           
    
            self.getQsts().options = [x.getTitle() for x in currentQuiz.getQuestions()]   
               
            self.newquestionbox.layout.display = 'none'
            self.newquestionbox.layout.visibility = 'hidden'
            self.showquestionbox.layout.display = 'block'
            self.showquestionbox.layout.visibility = 'visible'
            self.getNewQuestButton().description  = "New Question"  
            self.NewQuestSave.layout.visibility = 'hidden'
            self.NewQuestSave.layout.display = 'none'
            self.EditQuest.layout.display = 'block'
            self.EditQuest.layout.visibility = 'visible'
                
                

        except Exception as e:             
            self.Progress.value +='ERROR: In saving new question .. '+str(e)+"\n"

        return

    def removeQuestion(self,b):

        try: 

            if currentQuiz.getCurrentQuestion() is None:
               return

            if currentQuiz.getCurrentQuestion() in self.getExamManager().getQuestionBank().getQuestions():
                self.getExamManager().getQuestionBank().getQuestions().remove(currentQuiz.getCurrentQuestion())

            if currentQuiz.getCurrentQuestion() in currentQuiz.getQuestions():
                currentQuiz.getQuestions().remove(currentQuiz.getCurrentQuestion())
                
            self.getExamManager().getQuestionBank().save_Questions(self.Progress)
            self.getQsts().options = [x.getTitle() for x in currentQuiz.getQuestions()]   

        except Exception as e:             
            self.Progress.value +='ERROR: In removing  question .. '+str(e)+"\n"

        return
        
        

    def generateQuizTab(self):

    
        separator = widgets.Box(layout=widgets.Layout(border='solid 1px lightblue', width='99%', height='1px', margin='5px 0px',style={'background': "#C7EFFF"}))
        vseparator = widgets.Box(layout=widgets.Layout(width='50px', height='99%', margin='5px 0px',style={'background': "#C7EFFF"}))

        self.NewQTxt.layout.width = '99%'
        self.NewQTxt.layout.height = '120px'
        self.NewQType.layout.margin = '5px 0px'
        self.NewQTopics.layout.width = '220px'
        self.NewQType.layout.width = '220px'


        choicebox = VBox(children=[self.choicebox1,self.choicebox2,self.choicebox3,self.choicebox4])
        choicebox.layout.width = '60%'
      
        expbox = VBox(children=[self.NewQExpTtl,self.NewQExp])
        self.NewQExp.layout.height = '90px'
        expbox.layout.height = choicebox.layout.height 
        

        
        self.newquestionbox = VBox(children=[HBox(children=[self.NewQTopics,self.NewQType,vseparator,self.NewQDate]),
                                             
                                             separator,HBox(children=[self.NewQTNameTtl,self.NewQName,self.Points]),separator,
                                             self.NewQTxtTtl,
                                             self.NewQTxt,
                                             HBox(children=[choicebox,expbox])])
                                    
                                 
        self.NewQuest.layout.width = self.Qqsts.layout.width
        self.RemoveQuest.layout.width = self.Qqsts.layout.width
        self.EditQuest.layout.width = self.Qqsts.layout.width
        self.NewQuestSave.layout.width = self.Qqsts.layout.width
        self.RemoveQuest.layout.height = '27px'
        self.EditQuest.layout.height = '27px'
        self.NewQuest.layout.height = '27px'

        self.NewQuestSave.layout.visibility = 'hidden'
        self.NewQuestSave.layout.display = 'none'


        hboxleft = VBox(children=[self.Tname,self.Topics,self.Qname,self.Qqsts,self.RemoveQuest,self.EditQuest,self.NewQuest,self.NewQuestSave],layout=Layout(width = '25%'))
        qvbox = VBox(children=[self.description_out,self.qans_lbl,self.writtenresp,self.choices])

       
        self.showquestionbox = VBox(children=[qvbox,self.check,self.feedback_out])
       
        self.titlebox = HBox(children=[self.CourseLbl,self.Teacher_lbl,self.teachers])

        self.QuizTab = VBox(children=[self.titlebox,HBox(children=[hboxleft,self.showquestionbox,self.newquestionbox]),self.Progress])

        self.Examlist.layout.width = '220px'
        self.NewExam.layout.height = '27px'
        self.AddQuest.layout.height = '27px'
        self.QNewExam.layout.height = '27px'
        self.NewExam.layout.width = self.Examlist.layout.width
        self.AddQuest.layout.width = self.Examlist.layout.width
        self.QNewExam.layout.width = self.Examlist.layout.width
       

        
        self.Examtopics.layout.width = self.Examlist.layout.width
        self.ExQqsts.layout.width = self.Examlist.layout.width
        self.ExQqsts.layout.height = '230px'


        self.QNewExam.layout.visibility = 'hidden' 
        self.QNewExam.layout.display = 'none'

        exambox = VBox(children=[self.Ename,self.Examlist,self.NewExam,self.QNewExam,self.AddQuest])

        examqsts = VBox(children=[self.Etopics,self.Examtopics,self.Exname,self.ExQqsts])
        examdetails = VBox(children=[self.exam_date])
        
        self.ExamInfobox = HBox(children=[examqsts])
        self.ExamInfobox2 = HBox(children=[examdetails])

       

    
        self.NewExamBox = VBox(children=[self.ExamName,self.ExamDate,self.ExamPoints])

        self.exmtitlebox = HBox(children=[self.CourseLbl])

        self.NewExamBox.layout.visibility = 'hidden' 
        self.NewExamBox.layout.display = 'none'

        
        
        leftmenu = VBox(children=[self.Tname,self.Topics,self.Qname,self.Qqsts],layout=Layout(width = '25%'))
        self.ExamTab = VBox(children=[self.exmtitlebox,HBox(children=[leftmenu,exambox,self.ExamInfobox,self.ExamInfobox2,self.NewExamBox])])
      
        self.newquestionbox.layout.visibility = 'hidden'
        self.showquestionbox.layout.visibility = 'hidden'

       
        return

    def applyqtype(self,b):

        nrchoices = 0

        if self.NewQType.value == "Two-choice":
            nrchoices = 2
        if self.NewQType.value == "Three-choice":
            nrchoices = 3
        if self.NewQType.value == "Four-choice":
            nrchoices = 4
    
        for i in range(nrchoices):
            myit = self.choicebxlist[i]
            myit.layout.display = 'block'
            myit.layout.visibility = 'visible'

        for j in range(nrchoices,4):
            myit = self.choicebxlist[j]
            myit.layout.display = 'none'
            myit.layout.visibility = 'hidden'
                


        return 
#############################################################################################################################
    def startNewQeustion(self,b):

        global ExamMngr

    
        self.Progress.value +="In new question function"+"\n"
        try: 
             # arguments: title, text, exp


            qstid = "NewQuestion"+"_"+str(len(ExamMngr.getQuestionBank().getQuestions()))+"_"+str((datetime.now().date()))
            
            newQuestion = Question(qstid,None,None,True,None)
            newQuestion.setTitle(self.getNewQTitle().value)
            newQuestion.setText(self.getNewQText().value)
            ExamMngr.getQuestionBank().setQuestionInPrep(newQuestion)
        except Exception as e:             
            print('ERROR: New question .. '+str(e))
       

        self.Progress.value +=" new question box: "+str(self.newquestionbox.layout.visibility)+"\n"
        self.Progress.value +=" showquestionbox: "+str(self.showquestionbox.layout.visibility)+"\n"

        if  self.getNewQuestButton().description != "Quit":
            self.getNewQTitle().value =  ""
            self.getNewQTopicsMenu().value = self.getNewQTopicsMenu().options[0]
            self.getNewQText().value = ""
           # self.getNewQTeacher().value = self.getNewQTeacher().options[0]
            self.getNewQExp().value = ""

        for j in range(4):
            self.choicelist[j][0].value = ""
            self.choicelist[j][1].value = False

        self.Progress.value +="button ... "+str(self.getNewQuestButton().description)+"\n"
        
        if  self.getNewQuestButton().description == "Quit":
            self.Progress.value +="quiting... "+str(self.showquestionbox.layout.visibility)+"\n"
            self.newquestionbox.layout.display = 'none'
            self.newquestionbox.layout.visibility = 'hidden'
            self.showquestionbox.layout.display = 'block'
            self.showquestionbox.layout.visibility = 'visible'
            self.getNewQuestButton().description  = "New Question"  
            self.NewQuestSave.layout.visibility = 'hidden'
            self.NewQuestSave.layout.display = 'none'
            self.EditQuest.layout.display = 'block'
            self.EditQuest.layout.visibility = 'visible'
              
        else:
            self.showquestionbox.layout.display = 'none'
            self.showquestionbox.layout.visibility = 'hidden'
            self.newquestionbox.layout.display = 'block'
            self.newquestionbox.layout.visibility = 'visible'
            self.getNewQuestButton().description = "Quit"   
            self.NewQuestSave.layout.display = 'block'
            self.NewQuestSave.layout.visibility = 'visible'
            self.EditQuest.layout.visibility = 'hidden'
            self.EditQuest.layout.display = 'none'

            
            
            nrchoices = 2
            for i in range(nrchoices):
                myit = self.choicebxlist[i]
                myit.layout.display = 'block'
                myit.layout.visibility = 'visible'

            for j in range(nrchoices,4):
                myit = self.choicebxlist[j]
                myit.layout.display = 'none'
                myit.layout.visibility = 'hidden'
                
       
          

        self.Progress.value +=" new question box: "+str(self.newquestionbox.layout.visibility)+"\n"
        self.Progress.value +=" showquestionbox: "+str(self.showquestionbox.layout.visibility)+"\n"
                
    
        return

    def editQuestion(self,b):

        if currentQuiz.getCurrentQuestion() == None:
            self.Progress.value +="no question selected to edit..."+"\n"
            return

        self.Progress.value +="editing question..."+"\n"
        try: 
            self.getExamManager().getQuestionBank().setQuestionInPrep(currentQuiz.getCurrentQuestion())
        except Exception as e:             
            print('ERROR: New question .. '+str(e))

        self.Progress.value +=" choices none?: "+str(self.getExamManager().getQuestionBank().getQuestionInPrep().getChoices == None)+"\n"
       

        self.Progress.value +=" new question box: "+str(self.newquestionbox.layout.visibility)+"\n"
        self.Progress.value +=" showquestionbox: "+str(self.showquestionbox.layout.visibility)+"\n"

        self.EditQuest.layout.visibility = 'hidden'
        self.EditQuest.layout.display = 'none'
        self.NewQuestSave.layout.visibility = 'hidden'
        self.NewQuestSave.layout.display = 'none'


        qstbank = self.getExamManager().getQuestionBank()



        if qstbank.getQuestionInPrep().getTitle()!= None:
            self.getNewQTitle().value =  str(qstbank.getQuestionInPrep().getTitle())


        self.Progress.value +=" properties applied: "+str(pd.isna(qstbank.getQuestionInPrep().getMainTopic()))+"\n"
        
        if (not pd.isna(qstbank.getQuestionInPrep().getMainTopic())):
            self.getNewQTopicsMenu().value = str(qstbank.getQuestionInPrep().getMainTopic())

        self.Progress.value +=" 3 "+"\n"   

        if qstbank.getQuestionInPrep().getText()!= None:
            self.getNewQText().value = str(qstbank.getQuestionInPrep().getText()) 

        self.Progress.value +=" 4 "+"\n"   

        #if qstbank.getQuestionInPrep().getTeacher()!= None:
        #    self.getNewQTeacher().value = str(qstbank.getQuestionInPrep().getTeacher())
            
        if str(qstbank.getQuestionInPrep().getExplanation()) != None :
            self.getNewQExp().value = str(qstbank.getQuestionInPrep().getExplanation())


     

     
        self.showquestionbox.layout.display = 'none'
        self.showquestionbox.layout.visibility = 'hidden'
        self.newquestionbox.layout.display = 'block'
        self.newquestionbox.layout.visibility = 'visible'
        self.getNewQuestButton().description = "Quit"   
        self.NewQuestSave.layout.display = 'block'
        self.NewQuestSave.layout.visibility = 'visible'


        for j in range(4):
            myit = self.choicebxlist[j]
            myit.layout.display = 'none'
            myit.layout.visibility = 'hidden'

        

        chid = 0
        for choice in self.getExamManager().getQuestionBank().getQuestionInPrep().getChoices():
            myit = self.choicebxlist[chid]
            myit.layout.display = 'block'
            myit.layout.visibility = 'visible'
            self.Progress.value +=" choice: "+str(choice[0])+"\n"
            self.choicelist[chid][0].value = choice[0]
            self.choicelist[chid][1].value = choice[1]
            chid+=1
            if chid > 3:
                break
            
         
     
        return

    def getQuizTab(self):
        return self.QuizTab

    def getExamTab(self):
        return self.ExamTab


    def findTopicQuestions(self,b):

        global currentQuiz,BOLD,RESET,QuestionTopics

        selected_topic = self.getTopics().value

        currentQuiz.getQuestions().clear()

        if selected_topic == "All":
            for myquest in self.getExamManager().getQuestionBank().getQuestions():
                currentQuiz.getQuestions().append(myquest)
        else:

            for myquest in self.getExamManager().getQuestionBank().getQuestions():
                if myquest.getMainTopic() == selected_topic:
                    currentQuiz.getQuestions().append(myquest)
        

        self.getQsts().options = [x.getTitle() for x in currentQuiz.getQuestions()]  

        

    ############################################################################################################################################
    def open_question(self,b):

        global currentQuiz,BOLD,RESET
        

        self.writtenresp.disabled = False
        self.writtenresp.value = ''

        self.showquestionbox.layout.display = 'block'
        self.showquestionbox.layout.visibility = 'visible'
       

        for qstn in currentQuiz.getQuestions():
            if qstn.getTitle() == self.Qqsts.value:
                currentQuiz.setCurrentQuestion(qstn)
                break

        if currentQuiz.getCurrentQuestion() is None:
           return
           
        try: 
            Qtitle = currentQuiz.getCurrentQuestion().getTitle()
            QText = currentQuiz.getCurrentQuestion().getText()
            QInfo= "" if currentQuiz.getCurrentQuestion().getTeacher() == None else "Teacher: "+str(currentQuiz.getCurrentQuestion().getTeacher())+""
            QInfo+= "" if currentQuiz.getCurrentQuestion().getMainTopic() == None else " | Topic: "+str(currentQuiz.getCurrentQuestion().getMainTopic())+""
            QInfo+= "" if currentQuiz.getCurrentQuestion().getDate() == None else " | Points: "+str(currentQuiz.getCurrentQuestion().getPoints())+""
            QInfo+= "" if currentQuiz.getCurrentQuestion().getDate() == None else " | Date: "+str(currentQuiz.getCurrentQuestion().getDate())+""
            with self.description_out:
                clear_output()
                print(f"""{BOLD}{Qtitle}{RESET}""",)
                if len(QInfo) > 1:
                    print(f"""{QInfo}{RESET}""",)
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
                if not pd.isna(currentQuiz.getCurrentQuestion().getExplanation()):
                    s+= currentQuiz.getCurrentQuestion().getExplanation()
               
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



def open_quiz(VisManager,online,DeelNo,tab_set):

    global currentQuiz,ExamMngr,VisualMngr

    ExamMngr = ExamManager("IB3502",online)
    VisManager.setExamManager(ExamMngr)
    VisualMngr = VisManager
  
        
    qtslist = []
    quizstr = "Quiz Deel "+str(DeelNo)+"_Questions"
    qname = "Questionbank"
        

    tab_set.set_title(0,qname); tab_set.set_title(1,"Exam Preparation")
    currentQuiz = Quiz(qname)

    VisualMngr.assignCurrentTeacher()


    VisManager.getQsts().options = [x.getTitle() for x in currentQuiz.getQuestions()]   

       
    return
##################################################################################################################################################


