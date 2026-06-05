"""Patch Projucer-generated BinaryData.cpp/.h with the new TUFAN assets
(no Projucer on this machine; symbol names stay identical so no code changes)."""
import re

REPO = r"C:\Users\drgos_5ax3dfg\Desktop\fxsound-app"
CPP = REPO + r"\fxsound\JuceLibraryCode\BinaryData.cpp"
H = REPO + r"\fxsound\JuceLibraryCode\BinaryData.h"
IMAGES = REPO + r"\fxsound\Images"

RESOURCES = {
    "logowhite_svg": IMAGES + r"\logo-white.svg",
    "logoblack_svg": IMAGES + r"\logo-black.svg",
    "logored_svg": IMAGES + r"\logo-red.svg",
    "logoblue_svg": IMAGES + r"\logo-blue.svg",
    "FxSound_White_Bars_svg": IMAGES + r"\FxSound White Bars.svg",
    "FxSound_Black_Bars_svg": IMAGES + r"\FxSound Black Bars.svg",
    "fxsound_png": IMAGES + r"\fxsound.png",
    "fxsound_large_png": IMAGES + r"\fxsound_large.png",
}

with open(CPP, "r", encoding="utf-8") as f:
    cpp = f.read()
with open(H, "r", encoding="utf-8") as f:
    h = f.read()

for symbol, path in RESOURCES.items():
    with open(path, "rb") as f:
        data = f.read()
    size = len(data)
    data += b"\x00"  # JUCE convention: null-terminated payload, Size excludes it

    m = re.search(rf"const char\* {symbol} = \(const char\*\) temp_binary_data_(\d+);", cpp)
    assert m, f"pointer def not found for {symbol}"
    n = m.group(1)

    nums = ",".join(str(b) for b in data)
    wrapped = "\n".join(nums[i:i + 240] for i in range(0, len(nums), 240))
    # re-wrap on comma boundaries to keep valid syntax
    lines, cur = [], ""
    for tok in nums.split(","):
        if len(cur) + len(tok) + 1 > 240:
            lines.append(cur.rstrip(","))
            cur = ""
        cur += tok + ","
    lines.append(cur.rstrip(","))
    body = "{ " + "\n".join(lines) + " };"

    # text resources are string literals, binary ones are numeric arrays -> replace
    # the entire span from array decl to pointer def with a numeric array (always valid)
    pat = re.compile(
        rf"static const unsigned char temp_binary_data_{n}\[\] =.*?"
        rf"const char\* {symbol} = \(const char\*\) temp_binary_data_{n};",
        re.DOTALL)
    repl = (f"static const unsigned char temp_binary_data_{n}[] =\n{body}\n\n"
            f"const char* {symbol} = (const char*) temp_binary_data_{n};")
    cpp, c1 = pat.subn(lambda _m: repl, cpp, count=1)
    assert c1 == 1, f"array block not patched for {symbol}"

    cpp, c2 = re.subn(rf"numBytes = \d+; return {symbol};", f"numBytes = {size}; return {symbol};", cpp, count=1)
    assert c2 == 1, f"getNamedResource not patched for {symbol}"

    h, c3 = re.subn(rf"const int\s+{symbol}Size = \d+;", f"const int            {symbol}Size = {size};", h, count=1)
    assert c3 == 1, f"header size not patched for {symbol}"
    print(f"{symbol}: temp_binary_data_{n}, {size} bytes")

with open(CPP, "w", encoding="utf-8", newline="\n") as f:
    f.write(cpp)
with open(H, "w", encoding="utf-8", newline="\n") as f:
    f.write(h)
print("BinaryData.cpp / BinaryData.h patched")
