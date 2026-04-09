import datetime
import importlib
importlib.reload(datetime)



def create_course(courseinfo):
    
    newcourse = Course(
        courseinfo['code'],
        courseinfo['naam'],
        courseinfo.get('startdatum',''),
        courseinfo.get('einddatum',''),
        courseinfo.get('voorkennisverplicht', []),
        courseinfo.get('voorkennisgewenst', []),
        courseinfo.get('tentamens', [])
    )

    return newcourse


class Start_and_enddate:
    """ Class for objects with a startdate and an enddate """
    def __init__(self, startdate=None, enddate=None):
        self.startdate = None
        self.enddate = None
        if startdate:
            self.startdate = datetime.date.fromisoformat(startdate)
        if enddate:
            self.enddate = datetime.date.fromisoformat(enddate)
       
    def __str__(self):
        """ String representation
        no startdate and enddate: returns variable
        otherwise: returns startdate,  enddate """
        if self.nodates():
            return 'variable'
        return str(self.startdate) + ', ' + str(self.enddate)

    def nodates(self):
        """ true when there is no startdate and no enddate """
        return (not self.startdate) and (not self.enddate)

    def quartile(self):
        """ Compute quartile
        startdate in month 9: return 1
        startdate in month 11: return 2
        startdate in month 2: return 3
        startdate in month 4: return 4
        otherwise: return -1
        """
        if self.nodates():
            return -1
        
        if self.startdate.month == 9:
            quartile = 1
        elif self.startdate.month == 11:
            quartile = 2
        elif self.startdate.month == 2:
            quartile = 3
        elif self.startdate.month == 4:
            quartile = 4
        else:
            quartile = -1
            
        return quartile


class Course:
    # TODO: implement and extend with attributes and methods

    def __init__(self, code, title, startdate=None, enddate=None, voorkennisverplicht=None, voorkennisgewenst=None, tentamens=None):
        self.code = code
        self.title = title
        self.start_and_enddate = Start_and_enddate(startdate, enddate)
        self.voorkennisverplicht = voorkennisverplicht or []
        self.voorkennisgewenst = voorkennisgewenst or []
        self.tentamens = tentamens or []
        return
    
    def getCode(self):
        return self.code

    def __str__(self):
        """ string with:
        - code,
        - title,
        - period,
        - new line
        - codes of required foreknowledge or 'geen verplichte voorkennis'
        - new line
        - codes of desired foreknowledge or 'geen gewenste voorkennis'
        - new line
        """
        line1 = 'code: ' + self.code + ', titel: ' + self.title + ', periode: ' + str(self.start_and_enddate.quartile())
        
        if self.voorkennisverplicht:
            line2 = 'verplichte voorkennis: ' + ', '.join(self.voorkennisverplicht)
        else:
            line2 = 'geen verplichte voorkennis'

        if self.voorkennisgewenst:
            line3 = 'gewenste voorkennis: ' + ', '.join(self.voorkennisgewenst)
        else:
            line3 = 'geen gewenste voorkennis'

        return line1 + '\n' + line2 + '\n' + line3

