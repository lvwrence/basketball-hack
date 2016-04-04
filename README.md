# unlock phone
adb shell input keyevent 82
# start fb messenger
adb shell monkey -p com.facebook.orca -c android.intent.category.LAUNCHER 1;

# press on first messenger
adb shell input tap 649 450

# open keyboard
adb shell input tap 367 1715

# open emojis
adb shell input tap 879 906

# go home
# adb shell input keyevent --longpress KEYCODE_L
