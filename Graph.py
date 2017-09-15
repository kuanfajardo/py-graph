import utils


class _Constraint:
	"""
	A constraint is an abstraction of a requirement on an object (Entity).

	It has a satisfaction clause, representing the conditions on the entity that cause the constraint to be satisfied.
	Whenever the the constraint is broken or satisfied, a response is triggered.

	Must be linked to an entity to be of any use.
	"""

	def __init__(self, identifier, clause, callback):
		"""
		Constraint constructor

		:param str identifier: constraint identifier type
		:param clause: function that takes an Entity as a parameter and returns a Boolean True if the constraint
				is satisfied, False otherwise
		:param callback: function that gets called every time the constraint CHANGES state
				(i.e. broken -> satisfied, satisfied -> broken)

		:return: None
		"""

		utils.assert_params([identifier, clause, callback], [str, callable, callable])

		self._value_changed = callback
		self.identifier = identifier
		self._satisfied = False
		self.clause = clause
		self.entity = None

	@property
	def satisfied(self):
		return self._satisfied

	@satisfied.setter
	def satisfied(self, value):
		utils.assert_type(value, bool)

		if self._satisfied != value:
			self._satisfied = value
			self._value_changed(self._satisfied)

	def satisfy(self):
		"""
		Set the constraint to "satisfied" calls callback function if previously broken.

		:return: None
		"""

		self.satisfied = True

	def fail(self):
		"""
		Set the constraint to "broken" calls callback function if previously satisfied.
		:return None
		"""

		self.satisfied = False

	def check(self):
		"""
		Checks the constraint for satisfaction (and sets the constraint to that value).
			Requires constraint to have been linked to an entity.

		:return: None
		:raises: TypeError if constraint has not been linked to en entity.
		"""

		if self.entity is None:
			raise Warning("Constraint cannot be checked if it has not been linked to an Entity")

		self.satisfied = self.clause(self.entity)

	def link_to(self, entity):
		"""
		Link the constraint to an Entity. Required in order to check the constraint. If already linked to an entity,
			does nothing.

		:param _Entity entity: entity to link constraint to
		:return: None
		"""

		utils.assert_type(entity, _Entity)

		if self.entity is None:
			self.entity = entity


class _Entity:
	"""
	An entity is an abstraction of an object that
		(1) has pre-determined, type-specific properties
		(2) can be constrained. These constraints are on the properties mentioned above.
	"""

	def __init__(self, identifier, property_map):
		"""
		Entity constructor creates an entity of type type with no constraints and no properties.

		:param str identifier: identifier of entity i.e. "subject", "person", "dog"
		:param dict property_map: dict<str, obj> map of entity properties (i.e. "name", "age") to their expected type
									(i.e. str, Map)

		:return:

		self.constraints: Array<_Constraint> - contains all Constraints linked to Entity

		"""

		utils.assert_params([identifier, property_map], [str, dict])

		self.identifier = identifier
		self.property_map = property_map
		self.constraints = []

	def __getitem__(self, item):
		utils.assert_type(item, str)
		return self.__dict__[item]

	def __setitem__(self, key, value):
		utils.assert_type(key, str)

		if key not in self.property_map:
			raise AttributeError("Entity of type " + self.identifier + " does not contain property \"" + key + "\"")

		expected_type = self.property_map[key]

		if type(value) != expected_type:
			raise TypeError(
				"Property \"" + key + "\" is of type \"" + expected_type + "\", not of \"" + type(value) + "\".")

		self.__dict__[key] = value

	def add_constraint(self, constraint):
		"""
		Add constraint to entity

		:param _Constraint constraint:
		:return: None
		"""
		utils.assert_type(constraint, _Constraint)

		self.constraints.append(constraint)
		constraint.check()

	def remove_constraint(self, constraint):
		"""
		Remove constraint from entity

		:param _Constraint constraint:
		:return: None
		"""
		utils.assert_type(constraint, _Constraint)

		if constraint in self.constraints:
			self.constraints.remove(constraint)


class Factory:
	"""
	Creates Constraint and Entity objects. In order to create Entity/Constraint objects, they must be registered via
	register_entity and register_constraint methods, respectively.
	"""

	def __init__(self):
		"""
		Factory constructor.
		"""

		self._entity_map = {}
		self._constraint_map = {}

	def register_entity(self, identifier, property_map):
		"""
		Register an identifier - property map pair for use in creating entities.

		:param str identifier: unique identifier describing entity type i.e. "class", "person", "subject"
		:param dict property_map: dictionary whose keys are names of entity properties (i.e. "name", "age"), and whose
			values are the expected type (i.e. str, int, dict) of that property. Note: to denote a first-class
			function as a type, use the "callable" keyword.
		:return: None
		"""

		utils.assert_params([identifier, property_map], [str, dict])

		if identifier not in self._entity_map:
			self._entity_map[identifier] = property_map

	def register_constraint(self, identifier, entity_type):
		"""
		Register an identifier - property map pair for use in creating entities.
		:param identifier: unique identifier describing constraint type
		:param entity_type: identifier of entity constraint is to be linked to; must have been registered
		:return: None
		:raises: AssertionError if entity_type is not registered
		"""

		utils.assert_params([identifier, entity_type], [str, str])

		if entity_type not in self._entity_map:
			raise AssertionError("Constraint entity_type is not registered")

		if identifier not in self._constraint_map:
			self._constraint_map[identifier] = entity_type

	def create_entity(self, identifier):
		"""
		Factory method for creating Entity objects.

		:param str identifier: identifier of Entity to create
		:return: Entity object of type identifier
		:raises: AttributeError if entity type is not registered.
		"""

		utils.assert_type(identifier, str)

		if identifier in self._entity_map:
			return _Entity(identifier, self._entity_map[identifier])

		raise AttributeError("Entity type \"" + identifier + "\" is not registered.")

	def create_constraint(self, identifier, clause, callback):
		"""
		Factory method for creating Constraint objects.

		:param str identifier: identifier of Constraint to create
		:param clause: function that takes an Entity object and returns a bool if the constraint is satisfied,
			false otherwise
		:param callback: function to be called when the constraint changes state; takes a boolean representing the
			constraint state (True -> satisfied, False -> not)
		:return: Constraint object of type identifier
		:raises: AttributeError if constraint type is not registered.
		"""

		utils.assert_params([identifier, clause, callback], [str, callable, callable])

		if identifier in self._constraint_map:
			return _Constraint(identifier, clause, callback)

		raise AttributeError("Constraint type \"" + identifier + "\" is not registered.")

	def link(self, a, b):
		"""
		Links a constraint to an entity.

		:param a: constraint or entity object
		:param b: constraint or entity object; must be of different type than a
		:return: None
		:raises: AttributeError if type of entity is not the registered "companion" type of the given constraint type.
		"""

		constraint = a if type(a) == _Constraint else b
		entity = a if constraint is b else b

		utils.assert_params([constraint, entity], [_Constraint, _Entity])

		if self._constraint_map[constraint.identifier] != entity.identifier:
			raise AttributeError(
				"Constraint of type \"" + constraint.identifier + "\" can only be linked to Entity of type \"" +
				self._constraint_map[constraint.identifier] + "\"." + "Tried to link to Entity of type \"" +
				entity.identifier + "\".")

		constraint.link_to(entity)
		entity.add_constraint(constraint)

		constraint.check()


class Graph:

	def __init__(self, name):
		"""
		Graph constructor.

		:param str name: name of graph
		:return: Empty Graph object.
		"""

		self.name = name
		self._entities = set()
		self._constraints = set()

	@property
	def entities(self):
		return self._entities

	@entities.setter
	def entities(self, value):
		raise NotImplementedError("Cannot reassign entities of graph")

	@property
	def constraints(self):
		return self._constraints

	@constraints.setter
	def constraints(self, value):
		raise NotImplementedError("Cannot reassign constraints of graph")

	def add(self, obj):
		"""
		Add a constraint or entity to the graph. If already added, does nothing. If obj is a Constraint, also adds its
		 linked Entity to the graph. If obj is an Entity, also adds all of its constraints to graph.

		:param obj: Constraint or Entity object to add.
		:return: None
		:raises: AssertionError is obj is of Constraint type and it is unlinked.
		"""

		if type(obj) == _Entity:
			self._entities.add(obj)

			for constraint in obj.constraints:
				self.add(constraint)

		if type(obj) == _Constraint:
			self._constraints.add(obj)

			if obj.entity is not None:
				raise AssertionError("Cannot add unlinked constraint to graph.")

			self._entities.add(obj.entity)

	def remove(self, obj):
		"""
		Remove a constraint or entity from graph.

		:param obj: Constraint or Entity object to remove from graph. If obj is an Entity, removes all of its
			constraints from graph as well.

		:return: None
		"""

		if type(obj) == _Entity:
			self._entities.remove(obj)

			for constraint in obj.constraints:
				self.remove(constraint)

		if type(obj) == _Constraint:
			self._constraints.remove(obj)

			# TODO: delete constraint from Entity? remove Entity if has no constraint?

	def __contains__(self, item):
		if type(item) == _Entity:
			return item in self._entities

		if type(item) == _Constraint:
			return item in self._constraints

	def __str__(self):
		return self.name + "\n\t" + \
			str(len(self._entities)) + " entities\n\t" + \
			str(len(self._constraints)) + " constraints."
