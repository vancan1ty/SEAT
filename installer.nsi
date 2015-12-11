;Currell Berry
;TODO
;3. test on a couple different platforms. MEH
;8. go through and make sure bundled msys has all advertised features. HARDISH.

!include "MUI2.nsh"
!include nsDialogs.nsh
!include LogicLib.nsh
!include x64.nsh

Name "Simple EEG Analysis Tool"
Icon "images\SEAT_logo.ico"
!define MUI_ICON "images\SEAT_logo.ico"

OutFile "SEAT.exe"
!define VERSIONMAJOR 1
!define VERSIONMINOR 1
!define VERSIONBUILD 1
!define DESCRIPTION "Simple EEG Analysis Tool."

;default location where SEAT itself will be installed
InstallDir "$PROGRAMFILES\SEAT"
;Get installation folder from registry if available
InstallDirRegKey HKCU "Software\SEAT" ""

!define SEATINSTALLDIR $INSTDIR

RequestExecutionLevel admin ;Require admin rights on NT6+ 
 
# These will be displayed by the "Click here for support information" link in "Add/Remove Programs"
# It is possible to use "mailto:" links in here to open the email client
!define HELPURL "https://github.com/vancan1ty/SEAT"
!define UPDATEURL "https://github.com/vancan1ty/SEAT"
!define ABOUTURL "https://github.com/vancan1ty/SEAT"

# This is the approximate size (in kB) of all the files copied into "Program Files"
!define INSTALLSIZE 230000

!define MUI_ABORTWARNING
 
# rtf or txt file - remember if it is txt, it must be in the DOS text format (\r\n)
LicenseData "LICENSE"

;--------------------------------
;Pages

;LangString welcome_str ${LANG_ENGLISH} "This wizard will guide you through the installation of Simple EEG Analysis Tool (SEAT).$\r$\n$\r$\nSEAT provides a simple environment, based on MNE-Python, to visualize and interact with EEG data. This installer will install SEAT, and optionally its dependencies including Python, on this computer.$\r$\n$\r$\nIt is recommended that you close all other applications before starting Setup.  This will make it possible to update relevant system files without having to reboot your computer$\r$\n$\r$\nClick next to continue."
;!define MUI_WELCOMEPAGE_TEXT $(welcome_str)
!insertmacro MUI_PAGE_WELCOME 

Page custom myCheckPage

!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_COMPONENTS

Page custom myConfirmPage

!define MUI_PAGE_CUSTOMFUNCTION_LEAVE BroadcastPathChanges
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM

!define MUI_PAGE_CUSTOMFUNCTION_LEAVE un.BroadcastPathChanges
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
  
;--------------------------------
Var Dialog
Var Label
;Var Text

Function myCheckPage
    nsDialogs::Create 1018
    Pop $Dialog

    ${If} $Dialog == error
	    Abort
    ${EndIf}

   !insertmacro MUI_HEADER_TEXT "Installation Note" ""

   ${NSD_CreateLabel} 0 0 100% -2u "If you opt for the integrated python install, do not change the directory into which Python installs itself (C:\Miniconda2)."
   Pop $Label

   ;${NSD_CreateText} 0 13u 100% -13u "Type something here..."
   ;Pop $Text

   ${If} ${RunningX64}
   
   ${Else}
           MessageBox MB_OK|MB_ICONSTOP   "The SEAT installer only works for 64 bit windows.  You will have to install SEAT manually."
           Quit
   ${EndIf}    

   nsDialogs::Show

FunctionEnd

Function myConfirmPage
    nsDialogs::Create 1018
    Pop $Dialog

    ${If} $Dialog == error
	    Abort
    ${EndIf}

   # 64 bit code
   !insertmacro MUI_HEADER_TEXT "Confirm Installation" "Review Changes"

   ${NSD_CreateLabel} 0 0 100% -2u "When you click 'Install', one of the following two things will happen, depending on your choice in the previous step.$\r$\n$\r$\n.A: You selected 'Install Python & Dependencies'$\r$\n1. 'Miniconda' python distribution will be installed at C:/Anaconda.$\r$\n2. Necessary python dependencies, including Scipy, Numpy, and MNE, will be downloaded and installed$\r$\n3. SEAT files and uninstaller will be installed in ${SEATINSTALLDIR}$\r$\n$\r$\nB:You did not select 'Install Python & Dependencies' on the previous screen:$\r$\n1. SEAT files and unisntaller will be installed in ${SEATINSTALLDIR}$\r$\n$\r$\nIf for any reason you are not satisfied you can always run the SEAT uninstaller, followd by the Miniconda uninstaller, to revert all changes."
   Pop $Label

   ;${NSD_CreateText} 0 13u 100% -13u "Type something here..."
   ;Pop $Text

   nsDialogs::Show
FunctionEnd

InstType "Full (Installs SEAT+Python in standard locations)"
 
;------------ functions and macros --------------
function .onInit
	setShellVarContext all
functionEnd
;----------------------------------------------------------
 
;global section, installs miniconda reg keys and such.
Section 
	SectionIn 1
	# Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
	setOutPath $INSTDIR

	# Files added here should be removed by the uninstaller (see section "uninstall")
	file "README.md"
	file /r "images"
 
	# Uninstaller - See function un.onInit and section "uninstall" for configuration
	writeUninstaller "$INSTDIR\uninstall.exe"
 
	# Start Menu
	createDirectory "$SMPROGRAMS\SEAT"
	createShortCut "$SMPROGRAMS\SEAT\SEAT_uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\images\SEAT_logo_uninstall.ico"

	# Registry information for add/remove programs
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "DisplayName" "SEAT ${DESCRIPTION}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "InstallLocation" "$\"$INSTDIR$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "DisplayIcon" "$\"$INSTDIR\images\SEAT_logo.ico$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "Publisher" "$\"SEAT$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "HelpLink" "$\"${HELPURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "URLUpdateInfo" "$\"${UPDATEURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "URLInfoAbout" "$\"${ABOUTURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "DisplayVersion" "$\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}$\""
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "VersionMajor" ${VERSIONMAJOR}
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "VersionMinor" ${VERSIONMINOR}
	# There is no option for modifying or repairing the install
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "NoModify" 1
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "NoRepair" 1
	# Set the INSTALLSIZE constant (!defined at the top of this script) so Add/Remove Programs can accurately report the size
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT" "EstimatedSize" ${INSTALLSIZE}

SectionEnd

SectionGroup "SEAT" SEATGroup
  Section "SEAT 0.5" SEAT
	SectionIn 1
  	SetOutPath "${SEATINSTALLDIR}"
	InitPluginsDir
	File /r "demodata"
	File /r "docs"
	File /r "images"
	File /r "studies"
	File /r "wavelets"
	File "CanvasHandler.py"
	File "DataProcessing.py"
	File "EEGScrollArea.py"
	File "FixedSys.bmp"
	File "LICENSE"
	File "LineDrawer.py"
	File "QIPythonWidget.py"
	File "README.md"
	File "SEAT.bat"
	File "TextDrawer.py"

	createShortCut "$SMPROGRAMS\SEAT\SEAT.lnk" "${SEATINSTALLDIR}\SEAT.bat" "" "$INSTDIR\images\SEAT_logo.ico"
SectionEnd
 
Section "Add SEAT to PATH" SEAT_PATH_SECTION
  	  SectionIn 1

  	  Push "${SEATINSTALLDIR}"
  	  Call AddToPath
SectionEnd

;Section "Add 'open with SEAT' option to context menu" SEAT_CTX_SECTION
;  	  SectionIn 1
;
;               ;CB the below does not work.  Anyway, I don't want to mess with the Registry keys for EDF files,
;               ;in case users have other software are installed.
;	 ;WriteRegStr HKCR ".edf\OpenWithList\SEAT.bat" "" '${SEATINSTALLDIR}\SEAT.bat -f "%1"' ;CB not at all sure this will work. 
;
;  	  Push "${SEATINSTALLDIR}\bin"
;  	  Call AddToPath
;SectionEnd


SectionGroupEnd

SectionGroup "Python&SEAT Dependencies" depsGroup
    Section "Python and Dependencies" Python
	SectionIn 1
	SetOutPath "${SEATINSTALLDIR}"

	File /r "installer_dependencies"
              
              ExecWait '"$INSTDIR\installer_dependencies\Miniconda-latest-Windows-x86_64.exe"' $0
              ${If} $0 != 0 
	   DetailPrint "$0" ;print error message to log
                 MessageBox MB_OK|MB_ICONSTOP   "Miniconda installation failed."
              ${EndIf}

              ExecWait '"C:\Miniconda2\Scripts\conda.exe" install pip numpy scipy vispy pyqt ipython' $0
              ${If} $0 != 0 
	   DetailPrint "$0" ;print error message to log
                 MessageBox MB_OK|MB_ICONSTOP   "Conda packages installation failed.  You will have to fix the installation to make it work."
              ${EndIf}

              ExecWait '"C:\Miniconda2\Scripts\pip.exe" install mne'
              ${If} $0 != 0 
	   DetailPrint "$0" ;print error message to log
                 MessageBox MB_OK|MB_ICONSTOP   "MNE installation failed.  You will have to fix the installation to make it work."
              ${EndIf}

	;delete "${SEATINSTALLDIR}\Miniconda-latest-Windows-x86-64.exe"

    SectionEnd

SectionGroupEnd

;--------------------------------
;Descriptions

;Language strings
LangString DESC_SEAT ${LANG_ENGLISH} "Install and configure SEAT."
LangString DESC_Python ${LANG_ENGLISH} "Install Python and SEAT Dependencies."

;Assign language strings to sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	     !insertmacro MUI_DESCRIPTION_TEXT ${SEAT} $(DESC_SEAT)
	     !insertmacro MUI_DESCRIPTION_TEXT ${Python} $(DESC_Python)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------

# Uninstaller
 
;function un.onInit
;	!insertmacro VerifyUserIsAdmin
;functionEnd

Section "Uninstall"
  	SetShellVarContext all
	delete "$SMPROGRAMS\SEAT\SEAT.lnk"
	delete "$SMPROGRAMS\SEAT\SEAT_uninstall.lnk"
	
	# Remove files
	delete $INSTDIR\README.md
	RMDir /r $INSTDIR\images
	RMDir /r "${SEATINSTALLDIR}"

	# Remove Start Menu launcher
	# Try to remove the Start Menu folder - this will only happen if it is empty
	DetailPrint "attempt removal of  $SMPROGRAMS\SEAT"
	RMDir "$SMPROGRAMS\SEAT"

  	; Remove SEAT install dir from PATH
  	Push "${SEATINSTALLDIR}\bin"
  	Call un.RemoveFromPath

	RMDir /r "${SEATINSTALLDIR}"

	Delete $INSTDIR\Uninstall.exe
	
	RMDir $INSTDIR

	;DeleteRegKey HKCR ".edf\OpenWithList\SEAT.bat" 
	
	DeleteRegKey /ifempty HKCU "Software\SEAT"
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SEAT"
SectionEnd

;--------------------------------------------------------------------
; Path functions
;
; Based on example from:
; http://nsis.sourceforge.net/Path_Manipulation
; taken from smartmontools installer
; http://www.smartmontools.org/browser/trunk/smartmontools/os_win32/installer.nsi?rev=4110&order=name
;

!include "WinMessages.nsh"

; Registry Entry for environment (NT4,2000,XP)
; All users:
!define Environ 'HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"'
; Current user only:
;!define Environ 'HKCU "Environment"'

; AddToPath - Appends dir to PATH
;   (does not work on Win9x/ME)
;
; Usage:
;   Push "dir"
;   Call AddToPath

Function AddToPath
  Exch $0
  Push $1
  Push $2
  Push $3
  Push $4

  ; NSIS ReadRegStr returns empty string on string overflow
  ; Native calls are used here to check actual length of PATH

  ; $4 = RegOpenKey(HKEY_LOCAL_MACHINE,   "SYSTEM\CurrentControlSet\Control\Session Manager\Environment", &$3)
  System::Call "advapi32::RegOpenKey(i 0x80000002, t'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', *i.r3) i.r4"
  IntCmp $4 0 0 done done
  ; $4 = RegQueryValueEx($3, "PATH", (DWORD*)0, (DWORD*)0, &$1, ($2=NSIS_MAX_STRLEN, &$2))
  ; RegCloseKey($3)
  System::Call "advapi32::RegQueryValueEx(i $3, t'PATH', i 0, i 0, t.r1, *i ${NSIS_MAX_STRLEN} r2) i.r4"
  System::Call "advapi32::RegCloseKey(i $3)"

  IntCmp $4 234 0 +4 +4 ; $4 == ERROR_MORE_DATA
    DetailPrint "AddToPath: original length $2 > ${NSIS_MAX_STRLEN}"
    MessageBox MB_OK "PATH not updated, original length $2 > ${NSIS_MAX_STRLEN}"
    Goto done

  IntCmp $4 0 +5 ; $4 != NO_ERROR
    IntCmp $4 2 +3 ; $4 != ERROR_FILE_NOT_FOUND
      DetailPrint "AddToPath: unexpected error code $4"
      Goto done
    StrCpy $1 ""


  ; Check if already in PATH
  Push "$1;"
  Push "$0;"
  Call StrStr
  Pop $2
  StrCmp $2 "" 0 done
  Push "$1;"
  Push "$0\;"
  Call StrStr
  Pop $2
  StrCmp $2 "" 0 done

  ; Prevent NSIS string overflow
  StrLen $2 $0
  StrLen $3 $1
  IntOp $2 $2 + $3
  IntOp $2 $2 + 2 ; $2 = strlen(dir) + strlen(PATH) + sizeof(";")
  IntCmp $2 ${NSIS_MAX_STRLEN} +4 +4 0
    DetailPrint "AddToPath: new length $2 > ${NSIS_MAX_STRLEN}"
    MessageBox MB_OK "PATH not updated, new length $2 > ${NSIS_MAX_STRLEN}."
    Goto done


  ; Append dir to PATH
  DetailPrint "Add to PATH: $0"
  StrCpy $2 $1 1 -1
  StrCmp $2 ";" 0 +2
    StrCpy $1 $1 -1 ; remove trailing ';'
  StrCmp $1 "" +2   ; no leading ';'
    StrCpy $0 "$1;$0"
  WriteRegExpandStr ${Environ} "PATH" $0

done:
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Pop $0

  DetailPrint "finishing addToPath"
FunctionEnd


; RemoveFromPath - Removes dir from PATH
;
; Usage:
;   Push "dir"
;   Call RemoveFromPath

Function un.RemoveFromPath
  Exch $0
  Push $1
  Push $2
  Push $3
  Push $4
  Push $5
  Push $6

  ReadRegStr $1 ${Environ} "PATH"
  StrCpy $5 $1 1 -1
  StrCmp $5 ";" +2
    StrCpy $1 "$1;" ; ensure trailing ';'
  Push $1
  Push "$0;"
  Call un.StrStr
  Pop $2 ; pos of our dir
  StrCmp $2 "" done

  DetailPrint "Remove from PATH: $0"
  StrLen $3 "$0;"
  StrLen $4 $2
  StrCpy $5 $1 -$4 ; $5 is now the part before the path to remove
  StrCpy $6 $2 "" $3 ; $6 is now the part after the path to remove
  StrCpy $3 "$5$6"
  StrCpy $5 $3 1 -1
  StrCmp $5 ";" 0 +2
    StrCpy $3 $3 -1 ; remove trailing ';'
  WriteRegExpandStr ${Environ} "PATH" $3

done:
  Pop $6
  Pop $5
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Pop $0
FunctionEnd
 
var timer

; StrStr - find substring in a string
;
; Usage:
;   Push "this is some string"
;   Push "some"
;   Call StrStr
;   Pop $0 ; "some string"

!macro StrStr un
Function ${un}StrStr
  Exch $R1 ; $R1=substring, stack=[old$R1,string,...]
  Exch     ;                stack=[string,old$R1,...]
  Exch $R2 ; $R2=string,    stack=[old$R2,old$R1,...]
  Push $R3
  Push $R4
  Push $R5
  StrLen $R3 $R1
  StrCpy $R4 0
  ; $R1=substring, $R2=string, $R3=strlen(substring)
  ; $R4=count, $R5=tmp
  loop:
    StrCpy $R5 $R2 $R3 $R4
    StrCmp $R5 $R1 done
    StrCmp $R5 "" done
    IntOp $R4 $R4 + 1
    Goto loop
done:
  StrCpy $R1 $R2 "" $R4
  Pop $R5
  Pop $R4
  Pop $R3
  Pop $R2
  Exch $R1 ; $R1=old$R1, stack=[result,...]
FunctionEnd
!macroend
!insertmacro StrStr ""
!insertmacro StrStr "un."

;CB it appears that this is necessary for new cmd windows etc... to see the changed
;path items.  otherwise you have to completely reboot.
Function BroadcastPathChanges
  DetailPrint "broadcasting registry updates."
  SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=1500
  DetailPrint "Completed."
FunctionEnd

Function un.BroadcastPathChanges
  DetailPrint "broadcasting registry updates."
  SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=1500
  DetailPrint "Completed."
FunctionEnd
