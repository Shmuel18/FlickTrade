# Reset keyboard layout and run bot
$layout = "00000409"  # US English
[Runtime.InteropServices.Marshal]::GetActiveWindow() | Out-Null
Set-WinUILanguageOverride -Language en-US
python main.py
