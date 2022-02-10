test:  module_test functionnal_test

module_test: com_tests config_tests mydataclasses_tests

functionnal_test: server_tests

com_tests:
	python -m unittest discover -s com -v
config_tests:
	python -m unittest discover -s config -v
server_tests:
	python -m unittest discover -s server -v
mydataclasses_tests:
	python -m unittest discover -s mydataclasses -v
