from datetime import datetime

import peewee as pw
from tinydb import TinyDB, Query
import sys

# this json database indexed all employees' data
employee_db = TinyDB("employees.json")

# this SQL database keeps the ids of the employees who were sent for training, 
# together with its json data in a string, the start date, and a label.
training_db = pw.SqliteDatabase("training.db")

# this json database indexed the data of all employees sent for training
# with the start date, and the label from training_db
# (it has two extra fields compared to employee_db)
employee_sent_db = TinyDB("employees_sent_for_training.json")


"""
training_db's Training table schema

CREATE TABLE training (
    id INTEGER PRIMARY KEY, 
    employeeId TEXT UNIQUE, 
    employeeData TEXT
    trainingStartDate TEXT, 
    label TEXT, 
)
"""


class Training(pw.Model):
    employeeId = pw.CharField()
    employeeData = pw.CharField()   # json dump of the employee object from employee_db
    trainingStartDate = pw.DateField(default=datetime.now)
    label = pw.CharField(default='started')

    class Meta:
        database = training_db


#This function forms the query based on the argument passed.
def queryFormation(key,value,q):
    if key == "age_range":
        impl = ((q.age >= value[0] )& (q.age < value[1]))
    elif key =="keyword" :
        impl = (q.name.search(value) | q.jobTitle.search(value))
    elif key == "department_name":
        impl = (q.departmentName == value)
    else:
        impl = (q[key] == value)                   #This was not there in the previous code.I added this,if in case, in future we may need to check other variables also we can utilize this
    return impl
    

def create_employee_query(**criteria):
    """ create tinydb query for employee_db based on <criteria> 
        
        optional keyword args (at least one must be passed):
            age_range = (min age inclusive, max age exclusive)
            keyword = keyword to search against employee name and job title
            department_name = department name of the employee
    """
    if len(criteria) ==0:
        raise ValueError('This Method requires ateast one Argument to be passed')                   #when no argument is passed ,it will throw a ValueError
    q = Query()
    for index,(key,value) in enumerate (criteria.items()):
        if index == 0:
            impl = queryFormation(key,value,q)
        else:
            impl = impl | queryFormation(key,value,q)
    else:
        return impl                                                                                 # Once the query is formed ,it will be returned to the calling function
    


def send_employees_for_training(**criteria):
    """ search for employees with <criteria>, 
        create a record for each employee in training_db
        insert the records into employee_sent_db
        
        optional keyword args (at least one must be passed)::
            id = employee id, if this is used, all other keyword args are ignored

            age_range = (min age inclusive, max age exclusive)
            keyword = keyword to search against employee name and job title
            department_name = department name of the employee
    """
    if len(criteria) ==0:
        raise ValueError('This Method requires ateast one Argument to be passed')                     #when no argument is passed ,it will throw a ValueError
    else:
        if "ID" in criteria.keys():                                                                   #Condition to avoid other ID tags,If ID is present
            q=Query()
            impl = (q.id == criteria['ID'])
        else:
            impl = create_employee_query(**criteria)                                                  #Incase Id is not supplied,other parameters passed are considered for querying
        query_result_list = employee_db.search(impl)
        for query_result in query_result_list:
            if query_result!= None:
                element = Training()
                element.employeeId = query_result['id']
                element.employeeData = query_result
                try:
                    element.save()
                    for person in Training.select().where(Training.employeeId == query_result['id']):
                        query_result['label'] = person.label
                        query_result['trainingStartDate'] = str(person.trainingStartDate)
                    tmpdict ={}
                    for key,value in query_result.items():
                        tmpdict[key] = value    
                    employee_sent_db.insert(tmpdict)
                except:
                    print ("Unexpected error:", sys.exc_info())
                    print ("Exception occurred while Uploading ID",element.employeeId)
            else:
                raise ValueError('Wrong ID Passed|Record Does not exist in employees db')
