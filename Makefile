VERSION=1.2.0
RELEASE=1

check:
	env PYTHONPATH=$$PWD:$$PYTHONPATH DISPLAY= py.test \
	  --flakes \
	  --cov=qingfanyi \
	  --cov-report=term \
	  $(TESTARGS)

srpm: misc/spec/build/qingfanyi-$(VERSION)-$(RELEASE).el7.centos.src.rpm

misc/spec/build/qingfanyi-$(VERSION)-$(RELEASE).el7.centos.src.rpm: misc/spec/src/qingfanyi/v$(VERSION).tar.gz
	mock --resultdir $$(dirname $@) -r epel-7-x86_64 --buildsrpm --spec misc/spec/qingfanyi.spec --sources misc/spec/src/qingfanyi

misc/spec/src/qingfanyi/v$(VERSION).tar.gz:
	curl --fail -Lo $@ https://github.com/rohanpm/qingfanyi/archive/v$(VERSION).tar.gz
