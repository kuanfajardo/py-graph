from Graph import *

subjectMap = {
    "name": str,
    "number": str,
    "units": int
}

class Subject():
	def __init__(self, name, number):
		self.name = name
		self.number = number


g = Graph("TestGraph")

g.register_class(Subject)
g.register_entity("subject", subjectMap)

def clause(classNumber, className):
	def inner_clause(entity):
		return entity.number == classNumber and entity.name == className

	return inner_clause
	# return entity.number == "6.006"


def callback(satisfied):
	print(satisfied)

g.register_constraint("subject number", "Subject", clause)


#
# d = {
# 	"name": "Algorithms",
# 	"number": "6.006"
# }


s = Subject("Algorithms", "6.006")
subject = g.create_entity("Subject", s)


args = ("6.006", "Algorithms")
constraint = g.create_constraint("subject number", callback, *args)

print(constraint.satisfied)

