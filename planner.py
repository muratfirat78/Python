import course
import datetime
import importlib
importlib.reload(course)



class Planner:
    # TODO: implement and add attributes
    
    def __init__(self, application):
        self.application = application
        return

    def compute_current_state(self, course_done=None):
        self.application.done_course_codes.add(course_done)
        return

    def course_has_exam_end_of_quartile(self, course, quartile):
        quartile_to_month = {1: 11, 2: 2, 3: 4, 4: 9}
        target_month = quartile_to_month.get(quartile)
        if not target_month:
            return False

        for exam_date in course.tentamens:
            try:
                month = datetime.date.fromisoformat(exam_date).month
            except Exception:
                continue
            if month == target_month:
                return True
        return False

    def choose_course(self, quartile):
        """
        :param quartile: int that shows the quartile
        :return: string course code for this quartile
        """
        courses_in_quartile = []
        for course_list in self.application.available_courses.values():
            for course in course_list:
                if course.start_and_enddate.quartile() == quartile:
                    courses_in_quartile.append(course)
                elif course.start_and_enddate.quartile() == -1:
                    courses_in_quartile.append(course)

        """
        Remove courses which have already been done.
        """
        courses_in_quartile = [c for c in courses_in_quartile if c.getCode() not in self.application.done_course_codes]
        return courses_in_quartile

    def generate_for_quartile(self, quartile):
        """"
        Rules of engagement for course selection:
        1. The required prior knowledge of the chosen course must be met.
        2. The choice is made based on the following priorities:
           a. A fixed course takes precedence over a variable course.
           b. A course for which you have the desired prior knowledge takes precedence over a course for which you do not have the desired prior knowledge.
           c. A fiexed course that is part of the required prior knowledge of future courses taken of future courses takes precendence over other fixed courses.
           d. A fixed course that is part of the desired prior knowledge of future courses taken of future courses takes precendence thereafter.
           e. A variable course with an exam at the end of this quarter takes precedence over a variable course without such a suitable exam moment.
        """
        
        """
       :param quartile: int that shows the quartile
       :return: string for this quartile
       """
        #course_to_take = []
        course_to_take = self.choose_course(quartile)

        """
        Rule 1: The required prior knowledge of the chosen course must be met.
        Filter out courses for which the required prior knowledge is not met.
        """
        
        course_to_take = [c for c in course_to_take if set(c.voorkennisverplicht).issubset(self.application.done_course_codes)]

        """
        Rule 2a: A fixed course takes precedence over a variable course.
        """
        fixed_courses = [c for c in course_to_take if not c.start_and_enddate.nodates()]
        variable_courses = [c for c in course_to_take if c.start_and_enddate.nodates()]

        if fixed_courses:
            course_to_take = fixed_courses
        else:
            course_to_take = variable_courses

        """
        Rule 2b: A course for which you have the desired prior knowledge takes precedence over a course for which you do not have the desired prior knowledge.
        """
        courses_with_desired_prior_knowledge = [c for c in course_to_take if set(c.voorkennisgewenst).issubset(self.application.done_course_codes)]
        courses_without_desired_prior_knowledge = [c for c in course_to_take if not set(c.voorkennisgewenst).issubset(self.application.done_course_codes)]
        if courses_with_desired_prior_knowledge:
            course_to_take = courses_with_desired_prior_knowledge
        else:
            course_to_take = courses_without_desired_prior_knowledge

        """
        Rule 2c: A fixed course that is part of the required prior knowledge of future courses taken of future courses takes precendence over other fixed courses.
        """

        if fixed_courses:
            courses_with_required_prior_knowledge_of_future_courses = [c for c in fixed_courses if any(c.getCode() in future_course.voorkennisverplicht for course_list in self.application.available_courses.values() for future_course in course_list)]
            if courses_with_required_prior_knowledge_of_future_courses:
                course_to_take = courses_with_required_prior_knowledge_of_future_courses
            else:
                course_to_take = fixed_courses
    
        """
        Rule 2d: A fixed course that is part of the desired prior knowledge of future courses taken of future courses takes precendence thereafter.
        """
        if fixed_courses:
            courses_with_desired_prior_knowledge_of_future_courses = [c for c in fixed_courses if any(c.getCode() in future_course.voorkennisgewenst for course_list in self.application.available_courses.values() for future_course in course_list)]
            if courses_with_desired_prior_knowledge_of_future_courses:
                course_to_take = courses_with_desired_prior_knowledge_of_future_courses
            else:
                course_to_take = fixed_courses
        
        """
        Rule 2e: A variable course with an exam at the end of this quarter takes precedence over a variable course without such a suitable exam moment.
        """
        variable_courses = [c for c in course_to_take if c.start_and_enddate.nodates()]
        if variable_courses:
            courses_with_exam_at_end_of_quartile = [c for c in variable_courses if self.course_has_exam_end_of_quartile(c, quartile)]
            if courses_with_exam_at_end_of_quartile:
                course_to_take = courses_with_exam_at_end_of_quartile
            else:
                course_to_take = variable_courses

        return course_to_take[0].getCode() if course_to_take else None
    

    def generate(self):
        """
        :return: dictionary showing the course plan
        """
        Courses_to_take = dict() #key: quartile, val: course. 

        print(">>> Plan generation: Generate course plan...")

        quartile = 1
        
        while quartile <= 4:
            print(">>> quartile", quartile)
            quartile_course = self.generate_for_quartile(quartile)
            print(">>> course to take: ", str(quartile_course))

            if quartile_course:
                Courses_to_take[quartile] = quartile_course
                self.compute_current_state(quartile_course)

            quartile += 1

        return Courses_to_take
