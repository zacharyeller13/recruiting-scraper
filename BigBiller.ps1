### Important Pre-Requisites ###

# Get the ID and security principal of the current user account
$myWindowsID = [System.Security.Principal.WindowsIdentity]::GetCurrent();
$myWindowsPrincipal = New-Object System.Security.Principal.WindowsPrincipal($myWindowsID);

# Get the security principal for the administrator role
$adminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator;

# Check to see if we are currently running as an administrator
if ($myWindowsPrincipal.IsInRole($adminRole)) {
    # We are running as an administrator, so change the title and background colour to indicate this
    $Host.UI.RawUI.WindowTitle = $myInvocation.MyCommand.Definition + "(Elevated)";
    $Host.UI.RawUI.BackgroundColor = "DarkBlue";
    Clear-Host;
}
else {
    # We are not running as an administrator, so relaunch as administrator

    # Create a new process object that starts PowerShell
    $newProcess = New-Object System.Diagnostics.ProcessStartInfo "PowerShell";

    # Specify the current script path and name as a parameter with added scope and support for scripts with spaces in it's path
    $newProcess.Arguments = "& '" + $script:MyInvocation.MyCommand.Path + "'"

    # Indicate that the process should be elevated
    $newProcess.Verb = "runas";

    # Start the new process
    [System.Diagnostics.Process]::Start($newProcess);

    # Exit from the current, unelevated, process 
    Exit;
}

# Ensure SharepointPnP is installed
$arr = (Get-Module -ListAvailable | Format-Table Name -HideTableHeaders | Out-String) -split '\r?\n'
if (-Not @($arr) -like 'SharePointPnP*') {
    Install-Module -Name "SharepointPnPPowerShellOnline"
}

### Retrieve older file from Sharepoint ###

# Connect to Site
$siteUrl = 'https://jmtestsystemsinc.sharepoint.com/sites/FieldServices/Reporting'
Connect-PnPOnline -Url $siteUrl -Credentials 'O365Creds'

# Define folders & files
$folders = 'Shared Documents/','C:/Users/zacharye/Documents/PythonScripts/recruiting-scraper'
$file = 'tech_network.csv'

# Get old file from SharePoint
Get-PnPFile -Url (Join-Path $folders[0] $file) -Path $folders[1] -Filename $file -AsFile

### Scrape and Add New Data ###
$pythonScript = Join-Path $folders[1] 'BigBiller.py'
python $pythonScript

# Add file back to SharePoint
Add-PnPFile -Path (Join-Path $folders[1] $file) -Folder $folders[0]

# remove old file
Remove-Item (Join-Path $folders[1] $file)

Read-Host 'Success; press enter to exit...'