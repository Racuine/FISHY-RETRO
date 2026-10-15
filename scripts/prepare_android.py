
#!/usr/bin/env python3
"""Apply FISHY branding, fullscreen and Google OAuth to Android."""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
android = root / "android"

if not android.exists():
    raise SystemExit(
        "Android project missing: run npm run android:init first"
    )

res = android / "app/src/main/res"

# ============================================================
# 1. APP ICONS
# ============================================================

for dpi in ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"):
    d = res / f"mipmap-{dpi}"
    d.mkdir(parents=True, exist_ok=True)

    for name in (
        "ic_launcher.png",
        "ic_launcher_round.png",
        "ic_launcher_foreground.png"
    ):
        shutil.copyfile(
            root / "assets" / dpi / name,
            d / name
        )

# ============================================================
# 2. ADAPTIVE ICONS
# ============================================================

d = res / "mipmap-anydpi-v26"
d.mkdir(parents=True, exist_ok=True)

for name in ("ic_launcher.xml", "ic_launcher_round.xml"):
    (d / name).write_text(
        '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/fishy_icon_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
''',
        encoding="utf-8"
    )

# ============================================================
# 3. COLORS
# ============================================================

values = res / "values"
values.mkdir(parents=True, exist_ok=True)

(values / "fishy_colors.xml").write_text(
    '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="fishy_icon_background">#48B9E0</color>
</resources>
''',
    encoding="utf-8"
)

# ============================================================
# 4. SPLASH SCREEN
# ============================================================

drawable = res / "drawable"
drawable.mkdir(parents=True, exist_ok=True)

shutil.copyfile(
    root / "assets/splash.png",
    drawable / "fishy_splash.png"
)

(drawable / "fishy_launch.xml").write_text(
    '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@color/fishy_icon_background"/>
    <item
        android:gravity="center"
        android:drawable="@drawable/fishy_splash"/>
</layer-list>
''',
    encoding="utf-8"
)

# ============================================================
# 5. ANDROID THEME
# ============================================================

styles = values / "styles.xml"

if styles.exists():
    tree = ET.parse(styles)
    r = tree.getroot()

    for style in r.findall("style"):
        if style.attrib.get("name") == "AppTheme.NoActionBarLaunch":

            for item in list(style):
                if item.attrib.get("name") == "android:windowBackground":
                    style.remove(item)

            ET.SubElement(
                style,
                "item",
                {"name": "android:windowBackground"}
            ).text = "@drawable/fishy_launch"

    tree.write(
        styles,
        encoding="utf-8",
        xml_declaration=True
    )

# ============================================================
# 6. ANDROID 12+ SPLASH SCREEN
# ============================================================

v31 = res / "values-v31"
v31.mkdir(exist_ok=True)

(v31 / "fishy_splash.xml").write_text(
    '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style
        name="AppTheme.NoActionBarLaunch"
        parent="Theme.SplashScreen">

        <item name="windowSplashScreenBackground">
            @color/fishy_icon_background
        </item>

        <item name="windowSplashScreenAnimatedIcon">
            @drawable/fishy_splash
        </item>

        <item name="postSplashScreenTheme">
            @style/AppTheme.NoActionBar
        </item>

    </style>
</resources>
''',
    encoding="utf-8"
)

# ============================================================
# 7. IMMERSIVE FULLSCREEN
# ============================================================

java = (
    android
    / "app/src/main/java/com/fishyretro/game/MainActivity.java"
)

java.parent.mkdir(parents=True, exist_ok=True)

java.write_text(
    '''package com.fishyretro.game;

import android.os.Bundle;
import android.view.View;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);

        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
            View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
            View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
        );
    }

    @Override
    public void onWindowFocusChanged(boolean focused) {
        super.onWindowFocusChanged(focused);

        if (focused) {
            getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                View.SYSTEM_UI_FLAG_FULLSCREEN |
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            );
        }
    }
}
''',
    encoding="utf-8"
)

# ============================================================
# 8. GOOGLE OAUTH DEEP LINK
# ============================================================

manifest = android / "app/src/main/AndroidManifest.xml"

if not manifest.exists():
    raise SystemExit("AndroidManifest.xml not found")

ANDROID_NS = "http://schemas.android.com/apk/res/android"
ns = f"{{{ANDROID_NS}}}"

# Critical: preserve the android namespace when writing XML.
ET.register_namespace("android", ANDROID_NS)

tree = ET.parse(manifest)
manifest_root = tree.getroot()

application = manifest_root.find("application")

if application is None:
    raise SystemExit("Application element not found in manifest")

activity = None

for candidate in application.findall("activity"):
    if candidate.get(ns + "name") == ".MainActivity":
        activity = candidate
        break

if activity is None:
    raise SystemExit("MainActivity not found in manifest")

# Remove previous FISHY OAuth intent filters to avoid duplicates.
for intent in list(activity.findall("intent-filter")):
    remove = False

    for data in intent.findall("data"):
        scheme = data.get(ns + "scheme")
        host = data.get(ns + "host")

        if host == "auth" and scheme in (
            "fishyretro",
            "com.fishyretro.game"
        ):
            remove = True
            break

    if remove:
        activity.remove(intent)

# Add Google OAuth callback intent filter.
intent = ET.SubElement(activity, "intent-filter")

ET.SubElement(
    intent,
    "action",
    {ns + "name": "android.intent.action.VIEW"}
)

ET.SubElement(
    intent,
    "category",
    {ns + "name": "android.intent.category.DEFAULT"}
)

ET.SubElement(
    intent,
    "category",
    {ns + "name": "android.intent.category.BROWSABLE"}
)

ET.SubElement(
    intent,
    "data",
    {
        ns + "scheme": "fishyretro",
        ns + "host": "auth",
        ns + "path": "/callback"
    }
)

# Save the corrected manifest.
tree.write(
    manifest,
    encoding="utf-8",
    xml_declaration=True
)

# Validate the final XML.
ET.parse(manifest)

print("FISHY Android branding + fullscreen applied")
print("Google OAuth deep link: fishyretro://auth/callback")
print("AndroidManifest.xml validated successfully")
