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
APPLE_SIGNING_IDENTITY=$(shell awk -F "\"" '/APPLE_SIGNING_IDENTITY/ { print($$2); }' .env)
KEYCHAIN_PATH=~/Library/Keychains/login.keychain-db
NOTARIZATION_KEYCHAIN=$(shell awk -F "\"" '/NOTARIZATION_KEYCHAIN/ { print($$2); }' .env)
PYTHON_INTEL_VENV=~/Python-3_14_4-x86_64/bin/activate


all: ALWAYS
	make devrequirements
	make local
	make test
	make package
	make manpage
	make docs


app: ALWAYS
	make icons-mac
	pyinstaller --noconfirm --clean $(APP_NAME)_app.spec
	find $(DIST)/$(APP_BUNDLE) -type f \( -name "*.so" -o -name "*.dylib" \) -exec codesign --remove-signature {} \; 2>/dev/null || true
	@rm -rf $(DIST)/$(APP_NAME)
	@lipo -info $(DIST)/$(APP_BUNDLE)/Contents/MacOS/SSScore


mac: ALWAYS
	make DumbDriver
	make umountFlySight
	make app
	make app-intel
	make universal
	make notarize
	make dmg


app-intel: ALWAYS
	@echo "=== Building Intel/x86_64 bundle under Rosetta from arm64 venv ==="
	arch -x86_64 zsh -c 'source $(PYTHON_INTEL_VENV) && make -f Makefile.x86 app'


dmg:
	mkdir -p $(DMG_STAGING)
	for f in $(DIST)/*app; do cp -a "$$f" $(DMG_STAGING); done
	cp $(RESOURCES)/README.rtf $(DMG_STAGING)
	cd $(DMG_STAGING) && ln -sf /Applications ./Applications
	hdiutil create -volname $(DMG_NAME) -srcfolder $(DMG_STAGING) -ov -format ULMO -fs APFS $(DIST)/$(DMG_NAME)
	codesign --force --sign "$(APPLE_SIGNING_IDENTITY)" --timestamp --verbose=4 $(DIST)/$(DMG_NAME)
	codesign --verify --verbose $(DIST)/$(DMG_NAME)
	xcrun notarytool submit $(DIST)/$(DMG_NAME) --keychain-profile "$(NOTARIZATION_KEYCHAIN)" --wait
	xcrun stapler staple $(DIST)/$(DMG_NAME)
	spctl --assess --verbose --type open --context context:primary-signature $(DIST)/$(DMG_NAME)


universal: ALWAYS
	cp -a $(DIST)/$(APP_BUNDLE) $(DIST)/$(APP_BUNDLE_UNIVERSAL)
	./builduniversal $(DIST)/$(APP_BUNDLE) $(DIST)/$(APP_BUNDLE_INTEL) $(DIST)/$(APP_BUNDLE_UNIVERSAL)
	rm -Rf $(DIST)/$(APP_BUNDLE)
	mv $(DIST)/$(APP_BUNDLE_UNIVERSAL) $(DIST)/$(APP_BUNDLE)
	plutil -replace CFBundleIdentifier -string eu.ciurana.ssscoring.universal $(DIST)/$(APP_BUNDLE)/Contents/Info.plist
	rm -Rf $(DIST)/$(APP_BUNDLE_INTEL)
	./signapp $(DIST)/$(APP_BUNDLE) $(APP_ENTITLEMENTS)
	@lipo -info $(DIST)/$(APP_BUNDLE)/Contents/MacOS/SSScore

