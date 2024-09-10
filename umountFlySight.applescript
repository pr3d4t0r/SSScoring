-- BSD 3Clause License -- see LICENSE for details.
-- https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE
-- https://github.com/pr3d4t0r/SSScoring for full project.

-- Constants

property FLYSIGHT_SIG_FILE : "CONFIG.TXT"
property MOUNT_POINT : "/Volumes"
property OS : "Darwin"


-- Handlers

on die(msg, exitCode)
	display dialog msg buttons {"OK"}
	quit exitCode
end die


on assertMacOS()
	set currentOS to (do shell script "uname")
	if currentOS is not equal to OS then
		die("This tool is intended for macOS", 1)
	end if
end assertMacOS


on resolveFlySightMount()
	set mountPoints to paragraphs of (do shell script "ls " & quoted form of MOUNT_POINT)
	repeat with partialMountPoint in mountPoints
		set mountPoint to MOUNT_POINT & "/" & partialMountPoint
		set flagFile to mountPoint & "/" & FLYSIGHT_SIG_FILE
		set fileExists to (do shell script "test -e " & quoted form of flagFile & " && echo true || echo false")
		if fileExists is "true" then
			return mountPoint
		end if
	end repeat
	return ""
end resolveFlySightMount


on assertFlySightDirExists(directory)
	if directory is "" then
		die("no valid FlySight mount or directory found", 2)
	end if
	set dirExists to (do shell script "test -d " & quoted form of directory & " && echo true || echo false")
	if dirExists is "false" then
		die(directory & " does not exist; try again", 3)
	end if
end assertFlySightDirExists


on notifyUserWorkWith(msg)
	do shell script "osascript -e 'display notification \"" & msg & "\" with title \"umountFlySight\"'"
end notifyUserWorkWith


on ejectFlySight(mountPoint)
	set device to do shell script "mount | awk -v m=" & quoted form of mountPoint & " '$0 ~ m { print($1); }'"
	do shell script "diskutil unmountDisk " & quoted form of device
	set message to mountPoint & " device unmounted"
	notifyUserWorkWith(message)
end ejectFlySight


-- Main logic

assertMacOS()

set workDirectory to resolveFlySightMount()
assertFlySightDirExists(workDirectory)
notifyUserWorkWith("FlySight - eject FlySight mount " & workDirectory & return & "This operation may take a while")
ejectFlySight(workDirectory)

