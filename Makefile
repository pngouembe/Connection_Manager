test: resources_tests users_tests com_tests config_tests server_tests

resources_tests:
	python -m unittest discover -s resources -v
users_tests:
	python -m unittest discover -s users -v
com_tests:
	python -m unittest discover -s com -v
config_tests:
	python -m unittest discover -s config -v
server_tests:
	python -m unittest discover -s server -v
