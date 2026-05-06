# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

# Master Makefile -- Apple Silicon (arm64) macOS .app build.
#
# For Intel (x86_64) macOS:    activate86 && make -f Makefile.x86 <target>
# For Windows (later):         <activate-win-venv> && make -f Makefile.win <target>
#
# Arch-agnostic targets live in common.mk and are inherited unchanged.

include common.mk


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
	pyinstaller --noconfirm --clean SSScore_app.spec
	rm -rf $(DIST)/SSScore

