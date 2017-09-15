from Graph import *

f = Factory()

subjectMap = {
    "name": str,
    "number": str,
    "units": int
}

f.register_entity("subject", subjectMap)
f.register_constraint("name is Algorithms", "subject")

subject = f.create_entity("subject")
subject["number"] = "6.006"
subject["name"] = "Algorithms"


def clause(entity):
    return entity["name"] == "Algorithms"


def callback(satisfied):
    print(satisfied)

constraint = f.create_constraint("name is Algorithms", clause, callback)

f.link(subject, constraint) 

constraint.satisfy() 
constraint.fail()
constraint.check()
