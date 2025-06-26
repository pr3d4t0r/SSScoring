-- BSD 3Clause License -- see LICENSE for details.
-- https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE
-- https://github.com/pr3d4t0r/SSScoring for full project.


try
	-- Display confirmation dialog [1][5][7]
	set dialogResult to display dialog "This will unload the kernel extension: com.binaryfruit.driver.SATSMARTDriver" & return & return & "Requires administrator privileges." buttons {"Cancel", "Unload"} default button "Unload" with icon caution

	-- Execute command with secure authentication [1][4][5][8]
	if button returned of dialogResult is "Unload" then
		do shell script "/usr/bin/kmutil unload --bundle-identifier com.binaryfruit.driver.SATSMARTDriver" with administrator privileges
		display dialog "Kernel extension unloaded successfully." buttons {"OK"} default button "OK"
	end if
on error errMsg
	display dialog "Error: " & errMsg buttons {"OK"} with icon stop
end try

