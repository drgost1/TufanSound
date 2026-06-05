"""Rebrand all user-visible FxSound strings to TUFAN.
Internal identifiers, data paths, registry keys, the signed-driver device name
and GPL copyright headers are intentionally left untouched."""
import io

REPO = r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app"

EDITS = {
    r"fxsound\Source\GUI\FxMainWindow.cpp": [
        ('setName("FxSound");', 'setName("TUFAN");', 1),
    ],
    r"fxsound\Source\GUI\FxSystemTrayView.cpp": [
        ('TRANS("FxSound is %s.")', 'TRANS("TUFAN is %s.")', 1),
        ('lstrcpy(nid.szTip, L"FxSound");', 'lstrcpy(nid.szTip, L"TUFAN");', 1),
        ('String title = L"FxSound";', 'String title = L"TUFAN";', 1),
    ],
    r"fxsound\Source\GUI\FxController.cpp": [
        ('TRANS("Error in system audio configuration. Unable to run FxSound")',
         'TRANS("Error in system audio configuration. Unable to run TUFAN")', 1),
        ('FxMessage::showMessage(TRANS("FxSound is now open-source"), { TRANS("GitHub"), "https://github.com/fxsound2/fxsound-app" });',
         'FxMessage::showMessage(TRANS("TUFAN - powered by open-source FxSound"), { TRANS("GitHub"), "https://github.com/drgost1/TufanSound" });', 1),
        ('TRANS("FxSound in system tray\\r\\nClick FxSound icon to reopen")',
         'TRANS("TUFAN in system tray\\r\\nClick TUFAN icon to reopen")', 1),
        ('TRANS("Thanks for using FxSound! Would you be\\r\\ninterested in helping us by taking a quick 4 minute\\r\\nsurvey so we can make FxSound better?")',
         'TRANS("Thanks for using TUFAN! Would you be\\r\\ninterested in helping us by taking a quick 4 minute\\r\\nsurvey so we can make TUFAN better?")', 1),
        ('TRANS("FxSound is %s.")', 'TRANS("TUFAN is %s.")', 1),
    ],
    r"fxsound\Source\GUI\FxView.cpp": [
        ('TRANS("FxSound is unable to play processed audio',
         'TRANS("TUFAN is unable to play processed audio', 1),
    ],
    r"fxsound\JuceLibraryCode\JuceHeader.h": [
        ('projectName    = "FxSound";', 'projectName    = "TUFAN";', 1),
        ('companyName    = "FxSound LLC";', 'companyName    = "Tufan Studio";', 1),
    ],
    r"fxsound\Project\resources.rc": [
        ('VALUE "CompanyName",  "FxSound LLC\\0"', 'VALUE "CompanyName",  "Tufan Studio\\0"', 1),
        ('VALUE "LegalCopyright",  "2026 FxSound™\\0"',
         'VALUE "LegalCopyright",  "2026 FxSound LLC. TUFAN build by Tufan Studio (GPL-3.0)\\0"', 1),
        ('VALUE "FileDescription",  "FxSound\\0"', 'VALUE "FileDescription",  "TUFAN\\0"', 1),
        ('VALUE "ProductName",  "FxSound\\0"', 'VALUE "ProductName",  "TUFAN\\0"', 1),
    ],
    r"fxsound\ProjectARM\resources.rc": [
        ('VALUE "CompanyName",  "FxSound LLC\\0"', 'VALUE "CompanyName",  "Tufan Studio\\0"', 1),
        ('VALUE "LegalCopyright",  "2026 FxSound™\\0"',
         'VALUE "LegalCopyright",  "2026 FxSound LLC. TUFAN build by Tufan Studio (GPL-3.0)\\0"', 1),
        ('VALUE "FileDescription",  "FxSound\\0"', 'VALUE "FileDescription",  "TUFAN\\0"', 1),
        ('VALUE "ProductName",  "FxSound\\0"', 'VALUE "ProductName",  "TUFAN\\0"', 1),
    ],
    r"fxsound\FxSound.jucer": [
        ('name="FxSound" projectType="guiapp"', 'name="TUFAN" projectType="guiapp"', 1),
        ('companyName="FxSound LLC"', 'companyName="Tufan Studio"', 1),
    ],
}

for rel, edits in EDITS.items():
    path = REPO + "\\" + rel
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    for old, new, expected in edits:
        count = text.count(old)
        assert count == expected, f"{rel}: expected {expected}x, found {count}x: {old[:60]!r}"
        text = text.replace(old, new)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"patched {rel} ({len(edits)} edits)")
print("all string edits applied")
