<p align="center">
  <img src="branding/tufan-logo.png" width="220" alt="TUFAN logo">
</p>

<h1 align="center">TUFAN</h1>

<p align="center"><b>Personal audio-enhancer build for Windows, by Tufan Studio.</b><br>
A rebrand of the open-source <a href="https://github.com/fxsound2/fxsound-app">FxSound</a> app — same DSP engine, new identity.</p>

---

## What this is

TUFAN is a personal-use fork of [FxSound](https://github.com/fxsound2/fxsound-app) (GPL-3.0) with the
UI rebranded: new name, kitsune logo, wordmark, tray icons and version identity. All audio
processing, presets and the virtual-driver pipeline are unchanged.

**What was modified** (vs upstream `fxsound2/fxsound-app`):

- In-app header wordmark + theme logos (`fxsound/Images/*.svg`, re-embedded into `JuceLibraryCode/BinaryData.*`)
- Window / taskbar / tray icons (`fxsound/Project*/`: `icon.ico`, `white|red|gray|blue_logo.ico`)
- User-visible strings (window title, tray tooltip, notifications) → TUFAN
- `VERSIONINFO` resources + JUCE project identity
- Added GitHub Actions build workflow; removed upstream installer binary, funding + issue templates
- `branding/` holds the logo masters and the Python scripts that generated every asset

The virtual audio device keeps its original name **"FxSound Audio Enhancer"** — it ships inside a
code-signed driver that cannot be renamed without re-signing, and the app matches that exact string
at runtime ([`FxController.cpp`](fxsound/Source/GUI/FxController.cpp)).

## Run it

1. Install official FxSound once (from [fxsound.com](https://www.fxsound.com/) or
   [upstream releases](https://github.com/fxsound2/fxsound-app/releases)) — this installs the signed
   virtual audio driver TUFAN needs. You can quit/disable the stock app afterwards.
2. Download the `TUFAN-win-x64` artifact from this repo's
   [Actions](../../actions) (built automatically on every push).
3. Unzip and run `TUFAN.exe` (keep the preset folders next to the exe).

## Build from source

- Visual Studio 2022 with the **Desktop development with C++** workload
- [JUCE 6.1.6](https://github.com/juce-framework/JUCE/releases/tag/6.1.6) extracted to exactly
  `C:\JUCE` (hard-coded include path: `C:\JUCE\modules`)
- Open `fxsound/Project/FxSound.sln` → `Release | x64` → Build

Or just push to this repo — `.github/workflows/build.yml` does the above on a runner.

## License

GPL-3.0, same as upstream — see [LICENSE](LICENSE).
Original work © FxSound LLC. Modifications © 2026 Tufan Studio.
This is a personal-use build; it is not affiliated with or endorsed by FxSound LLC.
