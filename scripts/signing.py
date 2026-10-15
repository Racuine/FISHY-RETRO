from pathlib import Path
import os
p=Path('android/app/build.gradle')
keys=['ANDROID_KEYSTORE_PATH','ANDROID_KEYSTORE_PASSWORD','ANDROID_KEY_ALIAS','ANDROID_KEY_PASSWORD']
if not all(os.getenv(k) for k in keys):
 print('Signing secrets missing: release AAB will be unsigned. Debug APK will still build.')
else:
 with p.open('a') as f:
  f.write('''\nandroid {\n  signingConfigs {\n    fishyRelease {\n      storeFile file(System.getenv("ANDROID_KEYSTORE_PATH"))\n      storePassword System.getenv("ANDROID_KEYSTORE_PASSWORD")\n      keyAlias System.getenv("ANDROID_KEY_ALIAS")\n      keyPassword System.getenv("ANDROID_KEY_PASSWORD")\n    }\n  }\n  buildTypes { release { signingConfig signingConfigs.fishyRelease } }\n}\n''')
 print('Release signing enabled')
