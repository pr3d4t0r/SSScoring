-- AppleScript: Unload SATSMARTDriver with GUI
-- https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE

-- Check if the SATSMARTDriver is loaded
on isSATSMARTDriverLoaded()
    try
        set shellResult to do shell script "kmutil showloaded 2>&1 | awk '/SATSMARTDriver/'"
        if shellResult is not "" then
            return true
        end if
    end try
    return false
end isSATSMARTDriverLoaded


-- Show a warning dialog with confirmation
on requestUserConfirmation()
    display dialog "⚠️ The SATSMARTDriver kernel extension is currently loaded.

Unloading it while external devices are mounted may force umounting without recourse.
This can result in DATA LOSS — especially from encrypted volumes like those used by VeraCrypt.

Make sure all external devices are safely unmounted before continuing.

Do you want to unload the driver now?" with title "SATSMARTDriver Warning" buttons {"Cancel", "Unload"} default button "Unload" with icon caution
    set userChoice to button returned of the result
    if userChoice is equal to "Unload" then
        return true
    end if
    return false
end requestUserConfirmation


-- Rrun sudo command to unload the kernel module using AppleScript
on unloadSATSMARTDriver()
    set unloadCommand to "kmutil unload --bundle-identifier com.binaryfruit.driver.SATSMARTDriver"
    try
        do shell script unloadCommand with administrator privileges
        display dialog "✅ SATSMARTDriver was successfully unloaded." with title "Operation Complete" buttons {"OK"} default button "OK"
    on error errMsg number errNum
        display dialog "❌ Failed to unload SATSMARTDriver.\n\nError: " & errMsg with title "Error" buttons {"OK"} default button "OK"
    end try
end unloadSATSMARTDriver


-- main
if isSATSMARTDriverLoaded() then
    if requestUserConfirmation() then
        unloadSATSMARTDriver()
    else
        display dialog "Unload operation canceled by user." with title "Canceled" buttons {"OK"} default button "OK"
    end if
else
    display dialog "ℹ️ SATSMARTDriver is not currently loaded." with title "Driver Check" buttons {"OK"} default button "OK"
end if

