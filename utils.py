
def assert_type(obj, t):
	if t == callable:
		assert_callable(obj)
		return

	if not type(obj) == t:
		print(obj)
		raise TypeError()


def assert_params(params, types):
	assert len(params) == len(types)

	for i in range(len(params)):
		p = params[i]
		t = types[i]

		assert_type(p, t)


def assert_callable(function):
	if not callable(function):
		raise TypeError()
