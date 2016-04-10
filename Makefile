VERSION=1.2.0
RELEASE=1

SPEC_DIR=misc/spec
SRC_DIR=$(SPEC_DIR)/src
BUILD_DIR=$(SPEC_DIR)/build
SRC_TARBALL=$(SRC_DIR)/qingfanyi/v$(VERSION).tar.gz
SRC_URL=https://github.com/rohanpm/qingfanyi/archive/v$(VERSION).tar.gz
SRPM=$(BUILD_DIR)/qingfanyi-$(VERSION)-$(RELEASE).el7.centos.src.rpm

check:
	env PYTHONPATH=$$PWD:$$PYTHONPATH DISPLAY= py.test \
	  --flakes \
	  --cov=qingfanyi \
	  --cov-report=term \
	  $(TESTARGS)

srpm: $(SRPM)

$(SRPM): $(SRC_TARBALL)
	mock --resultdir $$(dirname $@) -r epel-7-x86_64 --buildsrpm --spec $(SPEC_DIR)/qingfanyi.spec --sources $(SRC_DIR)/qingfanyi

$(SRC_TARBALL):
	curl --fail -Lo $@ $(SRC_URL)

copr-build: $(SRPM)
	copr build qingfanyi $(SRPM)
