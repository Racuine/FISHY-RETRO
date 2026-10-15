#!/usr/bin/env python3
"""Apply FISHY branding and immersive mode to Capacitor-generated Android project."""
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
android=root/'android'
if not android.exists():
    raise SystemExit('Android project missing: run npm run android:init first')
res=android/'app/src/main/res'
for dpi in ('mdpi','hdpi','xhdpi','xxhdpi','xxxhdpi'):
    d=res/f'mipmap-{dpi}'
    d.mkdir(parents=True,exist_ok=True)
    for name in ('ic_launcher.png','ic_launcher_round.png','ic_launcher_foreground.png'):
        shutil.copyfile(root/'assets'/dpi/name,d/name)
# Adaptive icon is created by the Capacitor Android template; replace its colors and foreground.
for d in (res/'mipmap-anydpi-v26',):
    d.mkdir(parents=True,exist_ok=True)
    for name in ('ic_launcher.xml','ic_launcher_round.xml'):
        (d/name).write_text('''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/fishy_icon_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
''')
values=res/'values';values.mkdir(exist_ok=True)
(values/'fishy_colors.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<resources><color name="fishy_icon_background">#48B9E0</color></resources>''')
drawable=res/'drawable';drawable.mkdir(exist_ok=True)
shutil.copyfile(root/'assets/splash.png',drawable/'fishy_splash.png')
(drawable/'fishy_launch.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
<item android:drawable="@color/fishy_icon_background"/>
<item android:gravity="center" android:drawable="@drawable/fishy_splash"/>
</layer-list>''')
# Preserve Capacitor's generated theme and add a pre-Android-12 splash background.
styles=values/'styles.xml'
if styles.exists():
    tree=ET.parse(styles);r=tree.getroot()
    for style in r.findall('style'):
        if style.attrib.get('name')=='AppTheme.NoActionBarLaunch':
            for item in list(style):
                if item.attrib.get('name')=='android:windowBackground':style.remove(item)
            ET.SubElement(style,'item',{'name':'android:windowBackground'}).text='@drawable/fishy_launch'
    tree.write(styles,encoding='utf-8',xml_declaration=True)
# Android 12+ uses system splash screen; its icon is square and centered.
v31=res/'values-v31';v31.mkdir(exist_ok=True)
(v31/'fishy_splash.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<resources>
<style name="AppTheme.NoActionBarLaunch" parent="Theme.SplashScreen">
<item name="windowSplashScreenBackground">@color/fishy_icon_background</item>
<item name="windowSplashScreenAnimatedIcon">@drawable/fishy_splash</item>
<item name="postSplashScreenTheme">@style/AppTheme.NoActionBar</item>
</style>
</resources>''')
# Java activity is tiny; use Android immersive sticky flags without dependencies.
java=android/'app/src/main/java/com/fishyretro/game/MainActivity.java'
java.parent.mkdir(parents=True,exist_ok=True)
java.write_text('''package com.fishyretro.game;

import android.os.Bundle;
import android.view.View;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
            View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
            View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }
    @Override public void onWindowFocusChanged(boolean focused) {
        super.onWindowFocusChanged(focused);
        if (focused) getWindow().getDecorView().setSystemUiVisibility(
            5894 | View.SYSTEM_UI_FLAG_FULLSCREEN);
    }
}
''')
print('FISHY Android branding + fullscreen applied')

# Deep link for Supabase Google OAuth callback on Android.
manifest=android/'app/src/main/AndroidManifest.xml'
if manifest.exists():
    ns='{http://schemas.android.com/apk/res/android}'
    tree=ET.parse(manifest)
    application=tree.getroot().find('application')
    activity=application.find('activity') if application is not None else None
    if activity is not None:
        intent=ET.SubElement(activity,'intent-filter')
        ET.SubElement(intent,'action',{ns+'name':'android.intent.action.VIEW'})
        ET.SubElement(intent,'category',{ns+'name':'android.intent.category.DEFAULT'})
        ET.SubElement(intent,'category',{ns+'name':'android.intent.category.BROWSABLE'})
        ET.SubElement(intent,'data',{ns+'scheme':'com.fishyretro.game',ns+'host':'auth',ns+'pathPrefix':'/callback'})
        tree.write(manifest,encoding='utf-8',xml_declaration=True)
        print('Google OAuth Android deep link configured')
