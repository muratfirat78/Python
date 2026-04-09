import importlib
import pathlib
import json
import course
importlib.reload(course)
importlib.reload(pathlib) 
importlib.reload(json)


class DataManager:
    #COURSES_DONE_FILE = 'curssengedaan.json'
    
    def __init__(self, path=None):
        self.COURSES_DONE_FILE = ''    
        self.COURSES_OFFER_FILE = ''
        self.available_courses = dict() #key: course code, val: list of course objects
        self.done_course_codes = set() 
        if path:
            self.path = path
        else:
            self.path = pathlib.Path.cwd()
        self.done_codes = set()

    
    def ReadCourseData(self,testno):
        self.COURSES_DONE_FILE = ''

        print(">>>> Preparation phase: ReadCourseData, test case ",testno)
        
        if int(testno) == 0:
            self.COURSES_DONE_FILE = 'curssengedaan.json'    
        else:
            self.COURSES_DONE_FILE = 'test-'+str(testno)+'-curssengedaan.json'   
            
        self.COURSES_OFFER_FILE = 'cursusaanbod.json'
        
        print("Path: ",self.path)
        # Read courses done
        path = self.path / pathlib.Path(self.COURSES_DONE_FILE)
        file_path = pathlib.Path(path)
        print("File path: ",file_path)
        with file_path.open('r') as f:
            self.done_course_codes = set(json.load(f))
        
        # Read courses offered 
        path = self.path / pathlib.Path(self.COURSES_OFFER_FILE)
        file_path = pathlib.Path(path)
        with file_path.open('r') as f:
            for info in json.load(f):
                the_course = course.create_course(info)
                if not the_course.code in self.available_courses:
                    self.available_courses[the_course.code] = []
                self.available_courses[the_course.code].append(the_course)

        print(">>>> Taken courses: ",self.done_course_codes)
        print(">>>> Available courses: ",[c for c in self.available_courses.keys()])

                 
        return
        
        
        

   
  
      
 
               
    