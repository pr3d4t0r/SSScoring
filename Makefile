# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

# Master Makefile -- Apple Silicon (arm64) macOS .app build.
#
# For Intel (x86_64) macOS:    activate86 && make -f Makefile.x86 <target>
# For Windows (later):         <activate-win-venv> && make -f Makefile.win <target>
#
# Arch-agnostic targets live in common.mk and are inherited unchanged.

include common.mk

APP_BUNDLE="$(APP_NAME).app"
APP_ENTITLEMENTS=$(RESOURCES)/entitlements.plist


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
	codesign --deep --force --options=runtime --entitlements $(APP_ENTITLEMENTS) --sign "Developer ID Application: Eugene Ciurana (ZL73DA2Q97)" --preserve-metadata=identifier,entitlements,requirements,flags --timestamp $(DIST)/$(APP_BUNDLE)
	@rm -rf $(DIST)/$(APP_NAME)
	@lipo -info $(DIST)/$(APP_BUNDLE)/Contents/MacOS/SSScore

