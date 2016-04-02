check:
	env PYTHONPATH=$$PWD:$$PYTHONPATH DISPLAY= py.test \
	  --flakes \
	  --cov=qingfanyi \
	  --cov-report=term \
	  $(TESTARGS)
