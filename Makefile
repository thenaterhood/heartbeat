INSTALL_PATH ?= /
BUILD_PATH ?= build-heartbeat
INIT_SYSTEM ?= systemd
heartbeat:
	python3 setup.py install --prefix=$(BUILD_PATH) --record installed_files
	mkdir -p $(BUILD_PATH)/bin
	mkdir -p $(BUILD_PATH)/etc
	mkdir -p $(BUILD_PATH)/lib
	cp -r dist/_bin/* $(BUILD_PATH)/bin
ifneq ($(INIT_SYSTEM),systemd)
	@echo "==> Setting up for sysvinit"
	#cp -r dist/_etc/init.d $(BUILD_PATH)/etc
else
	@echo "==> Setting up for systemd"
	cp -r dist/_lib/* $(BUILD_PATH)/lib
endif
	cp dist/_etc/heartbeat.yml $(BUILD_PATH)/etc
	chmod +x $(BUILD_PATH)/bin/startheart
	@echo "A record of installed files is in installed_files."
clean:
	rm -r $(BUILD_PATH)

install:
	cp -r $(BUILD_PATH)/* $(INSTALL_PATH)

