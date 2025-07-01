-- BSD 3Clause License -- see LICENSE for details.
-- https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE
-- https://github.com/pr3d4t0r/SSScoring for full project.


-- Constants
property FLYSIGHT_SIG_FILE : "FLYSIGHT.TXT"
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


on resolveFlySightMounts()
    set flySightMounts to {}
    set mountPoints to paragraphs of (do shell script "ls -1 " & quoted form of MOUNT_POINT)

    repeat with partialMountPoint in mountPoints
        set mountPoint to MOUNT_POINT & "/" & partialMountPoint
        set flagFile to mountPoint & "/" & FLYSIGHT_SIG_FILE
        set fileExists to (do shell script "test -e " & quoted form of flagFile & " && echo true || echo false")

        if fileExists is "true" then
            set end of flySightMounts to mountPoint
        end if
    end repeat

    return flySightMounts
end resolveFlySightMounts


on notifyUserWorkWith(msg)
    do shell script "osascript -e 'display notification \"" & msg & "\" with title \"umountFlySight\"'"
end notifyUserWorkWith


on ejectFlySight(mountPoint)
    try
        set device to do shell script "mount | awk -v m=" & quoted form of mountPoint & " '$0 ~ m { print($1); }'"
        do shell script "diskutil unmountDisk " & quoted form of device
        set message to "Unmounted: " & mountPoint
        notifyUserWorkWith(message)
    on error errMsg
        set message to "Failed to eject " & mountPoint & ": " & errMsg
        notifyUserWorkWith(message)
    end try
end ejectFlySight


-- Main logic
assertMacOS()
set workDirectories to resolveFlySightMounts()

if (count of workDirectories) is 0 then
    die("No valid FlySight mounts found", 2)
end if

repeat with workDirectory in workDirectories
    notifyUserWorkWith("Processing FlySight mount: " & workDirectory)
    ejectFlySight(workDirectory)
end repeat

