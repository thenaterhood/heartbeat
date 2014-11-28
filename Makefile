heartbeat:
	@echo "Nothing to compile"
clean:
	@echo "Nothing to clean"

install:
	python3 setup.py install --prefix=$(INSTALL_PATH) --record installed_files
	mkdir -p $(INSTALL_PATH)/bin
	mkdir -p $(INSTALL_PATH)/etc
	cp -r dist/_bin/* $(INSTALL_PATH)/bin
	cp -r dist/_etc/* $(INSTALL_PATH)/etc
	chmod +x $(INSTALL_PATH)/bin/startheart
	@echo "A record of installed files is in installed_files."

