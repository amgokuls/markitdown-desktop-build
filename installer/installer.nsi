; MarkItDown Desktop — NSIS Installer Script
!include "MUI2.nsh"

; ROOT_DIR is passed in from the command line via /DROOT_DIR=...
!ifndef ROOT_DIR
  !define ROOT_DIR ".."
!endif

Name "MarkItDown Desktop"
OutFile "${ROOT_DIR}\installer\MarkItDown-Desktop-Setup.exe"
InstallDir "$PROGRAMFILES64\MarkItDown Desktop"
InstallDirRegKey HKCU "Software\MarkItDownDesktop" ""
RequestExecutionLevel admin

; Version info for Windows Explorer (reduces Smart App Control warnings)
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "MarkItDown Desktop"
VIAddVersionKey "CompanyName" "MarkItDown Desktop"
VIAddVersionKey "FileDescription" "MarkItDown Desktop Installer"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"
VIAddVersionKey "LegalCopyright" "Copyright 2026"

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "${ROOT_DIR}\resources\icons\AppIcon.ico"
!define MUI_UNICON "${ROOT_DIR}\resources\icons\AppIcon.ico"
!define MUI_WELCOMEPAGE_TITLE "Welcome to MarkItDown Desktop Setup"
!define MUI_WELCOMEPAGE_TEXT "This will install MarkItDown Desktop v1.0.0 on your computer.$\r$\n$\r$\nMarkItDown Desktop converts documents (PDF, Word, Excel, PowerPoint and more) to Markdown format.$\r$\n$\r$\nClick Next to continue."
!define MUI_FINISHPAGE_RUN "$INSTDIR\MarkItDown Desktop.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch MarkItDown Desktop now"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"

  ; Include the main executable and all its dependencies from dist folder
  File /r "${ROOT_DIR}\dist\MarkItDown Desktop\*.*"

  ; Create Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\MarkItDown Desktop"
  CreateShortcut "$SMPROGRAMS\MarkItDown Desktop\MarkItDown Desktop.lnk" "$INSTDIR\MarkItDown Desktop.exe"
  CreateShortcut "$SMPROGRAMS\MarkItDown Desktop\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  ; Create Desktop shortcut
  CreateShortcut "$DESKTOP\MarkItDown Desktop.lnk" "$INSTDIR\MarkItDown Desktop.exe"

  ; Write registry keys for Add/Remove Programs
  WriteRegStr HKCU "Software\MarkItDownDesktop" "" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarkItDownDesktop" "DisplayName" "MarkItDown Desktop"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarkItDownDesktop" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarkItDownDesktop" "DisplayIcon" "$INSTDIR\MarkItDown Desktop.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarkItDownDesktop" "Publisher" "MarkItDown Desktop"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarkItDownDesktop" "DisplayVersion" "1.0.0"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarkItDownDesktop" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarkItDownDesktop" "NoRepair" 1

  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\MarkItDown Desktop\MarkItDown Desktop.lnk"
  Delete "$SMPROGRAMS\MarkItDown Desktop\Uninstall.lnk"
  RMDir "$SMPROGRAMS\MarkItDown Desktop"
  Delete "$DESKTOP\MarkItDown Desktop.lnk"
  DeleteRegKey HKCU "Software\MarkItDownDesktop"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MarkItDownDesktop"
SectionEnd
