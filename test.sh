#!/bin/sh

test_py2() {
	python2     -m typedcollections.__init__
	python2     -m unittest typedcollections.test
	python2 -O  -m unittest typedcollections.test
	python2 -OO -m unittest typedcollections.test
}

test_py3() {
	python3     -m typedcollections.__init__
	python3     -m unittest typedcollections.test
	python3 -O  -m unittest typedcollections.test
	python3 -OO -m unittest typedcollections.test
}

case $1 in
	2)
		test_py2
		;;
	3)
		test_py3
		;;
	6)
		test_py2
		test_py3
		;;
	coverage)
		                 coverage run  -m --source typedcollections/ typedcollections.__init__
		                 coverage run -am --source typedcollections/ unittest typedcollections.test
		PYTHONOPTIMIZE=1 coverage run -am --source typedcollections/ unittest typedcollections.test
		PYTHONOPTIMIZE=2 coverage run -am --source typedcollections/ unittest typedcollections.test
		coverage report
		coverage html
		;;
esac
