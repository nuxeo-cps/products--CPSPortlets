.PHONY: check clean docs

check:
	pylint *.py

clean:
	find . "(" -name "*~" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f
	#rm -rf doc/API

docs:
	happydoc -d doc/API *.py
