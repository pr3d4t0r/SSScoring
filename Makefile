# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

# Master Makefile -- Apple Silicon (arm64) macOS .app build.
#
# For Intel (x86_64) macOS:    activate86 && make -f Makefile.x86 <target>
# For Windows (later):         <activate-win-venv> && make -f Makefile.win <target>
#
# Arch-agnostic targets live in common.mk and are inherited unchanged.

include common.mk

APP_BUNDLE=$(APP_NAME).app
APP_BUNDLE_INTEL=$(APP_NAME)-Intel.app
APP_BUNDLE_UNIVERSAL=$(APP_NAME)-Universal.app
APP_ENTITLEMENTS=$(RESOURCES)/entitlements.plist
KEYCHAIN_PATH=~/Library/Keychains/login.keychain-db


all: ALWAYS
	make devrequirements
	make local
	make test
	make package
	make manpage
	make docs
	make umountFlySight
	make DumbDriver
	make app


app: ALWAYS
	make icons-mac
	pyinstaller --noconfirm --clean $(APP_NAME)_app.spec
	find $(DIST)/$(APP_BUNDLE) -type f \( -name "*.so" -o -name "*.dylib" \) -exec codesign --remove-signature {} \; 2>/dev/null || true
	@rm -rf $(DIST)/$(APP_NAME)
	@lipo -info $(DIST)/$(APP_BUNDLE)/Contents/MacOS/SSScore


universal: ALWAYS
	cp -a $(DIST)/$(APP_BUNDLE) $(DIST)/$(APP_BUNDLE_UNIVERSAL)
	./builduniversal $(DIST)/$(APP_BUNDLE) $(DIST)/$(APP_BUNDLE_INTEL) $(DIST)/$(APP_BUNDLE_UNIVERSAL)
	rm -Rf $(DIST)/$(APP_BUNDLE)
	mv $(DIST)/$(APP_BUNDLE_UNIVERSAL) $(DIST)/$(APP_BUNDLE)
	plutil -replace CFBundleIdentifier -string eu.ciurana.ssscoring.universal $(DIST)/$(APP_BUNDLE)/Contents/Info.plist
	rm -Rf $(DIST)/$(APP_BUNDLE_INTEL)
	./signapp $(DIST)/$(APP_BUNDLE) $(APP_ENTITLEMENTS)
	@lipo -info $(DIST)/$(APP_BUNDLE)/Contents/MacOS/SSScore

