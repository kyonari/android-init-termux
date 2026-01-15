import os
import sys
import subprocess
import urllib.request
import shutil
import time
from pathlib import Path

# --- Konfigurasi ---
ANDROID_JAR_URL = "https://github.com/Sable/android-platforms/raw/master/android-34/android.jar"
MIN_SDK = 21
TARGET_SDK = 34

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message):
    print(f"{Colors.BLUE}[*] {message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}[+] {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}[!] {message}{Colors.ENDC}")

def check_dependencies():
    """Mengecek apakah tools yang dibutuhkan sudah terinstall di Termux"""
    tools = ["javac", "d8", "aapt2", "apksigner", "keytool", "zip"]
    missing = []
    
    print_status("Checking dependencies...")
    for tool in tools:
        if not shutil.which(tool):
            missing.append(tool)
    
    if missing:
        print_error(f"Tool berikut tidak ditemukan: {', '.join(missing)}")
        print(f"{Colors.WARNING}Silakan install paket yang dibutuhkan di Termux:{Colors.ENDC}")
        print(f"pkg install openjdk-17 android-tools")
        print(f"(Pastikan paket yang mengandung d8/dx terinstall, biasanya di android-tools atau dx)")
        sys.exit(1)
    print_success("Semua dependencies aman.")

def download_file_with_progress(url, filename):
    """Download file dengan progress bar sederhana"""
    try:
        print_status(f"Downloading {filename}...")
        start_time = time.time()
        
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\r{Colors.CYAN}Progress: [{('=' * (percent // 5)).ljust(20)}] {percent}%{Colors.ENDC}")
                sys.stdout.flush()

        urllib.request.urlretrieve(url, filename, reporthook)
        print() # Newline after progress
        print_success("Download complete.")
    except Exception as e:
        print_error(f"Download failed: {e}")
        sys.exit(1)

def create_android_project():
    print(f"{Colors.HEADER}{Colors.BOLD}=== Android Project Generator (Improved) ==={Colors.ENDC}")
    
    check_dependencies()

    # 1. Input User
    default_name = "MyTermuxApp"
    proj_input = input(f"{Colors.BOLD}Project Name (default: {default_name}): {Colors.ENDC}").strip()
    project_name = proj_input if proj_input else default_name
    
    # Validasi nama folder (hanya alfanumerik sederhana)
    project_name = "".join(x for x in project_name if x.isalnum() or x in "_-")

    default_pkg = "com.termux.app"
    pkg_input = input(f"{Colors.BOLD}Package Name (default: {default_pkg}): {Colors.ENDC}").strip()
    package_name = pkg_input if pkg_input else default_pkg

    # 2. Setup Direktori Utama
    project_path = Path(project_name)
    if project_path.exists():
        print(f"{Colors.WARNING}Folder '{project_name}' sudah ada!{Colors.ENDC}")
        if input("Overwrite/Continue? (y/n): ").lower() != 'y':
            return
    else:
        project_path.mkdir()

    # Pindah ke dalam folder project
    os.chdir(project_path)
    
    # Struktur Folder yang lebih rapi (Separate Logic)
    # src/main/java/com/package/...
    src_path = Path("src/main/java") / package_name.replace('.', '/')
    src_path.mkdir(parents=True, exist_ok=True)
    
    # Folder untuk output build (supaya tidak tercampur source code)
    Path("bin").mkdir(exist_ok=True)
    Path("lib").mkdir(exist_ok=True)

    print_success(f"Struktur folder dibuat di {project_name}/")

    # 3. Download android.jar ke folder lib
    android_jar_path = Path("lib/android.jar")
    if not android_jar_path.exists():
        download_file_with_progress(ANDROID_JAR_URL, str(android_jar_path))
    
    # 4. Buat Keystore
    keystore_path = "debug.keystore"
    if not os.path.exists(keystore_path):
        print_status("Generating Keystore...")
        cmd = [
            "keytool", "-genkey", "-v", 
            "-keystore", keystore_path, 
            "-storepass", "android", 
            "-alias", "androiddebugkey", 
            "-keypass", "android", 
            "-keyalg", "RSA", 
            "-keysize", "2048", 
            "-validity", "10000",
            "-dname", "CN=Android Debug,O=Android,C=US"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success("Keystore created.")

    # 5. AndroidManifest.xml
    manifest_content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">

    <uses-sdk android:minSdkVersion="{MIN_SDK}" android:targetSdkVersion="{TARGET_SDK}" />

    <application 
        android:label="{project_name}" 
        android:theme="@android:style/Theme.DeviceDefault.Light">
        <activity android:name=".MainActivity"
                  android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
    with open("AndroidManifest.xml", "w") as f:
        f.write(manifest_content)

    # 6. MainActivity.java
    java_content = f"""package {package_name};

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Button;
import android.widget.Toast;
import android.view.Gravity;
import android.graphics.Color;
import android.graphics.Typeface;

public class MainActivity extends Activity {{
    
    private int counter = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        // Layout Container
        var layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        layout.setBackgroundColor(Color.parseColor("#F0F0F0")); // Light Gray

        // Card Style Container
        var card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setGravity(Gravity.CENTER);
        card.setPadding(60, 60, 60, 60);
        card.setBackgroundColor(Color.WHITE);
        card.setElevation(10f);
        
        // Text Title
        var title = new TextView(this);
        title.setText("Pure Java UI");
        title.setTextSize(24f);
        title.setTypeface(null, Typeface.BOLD);
        title.setTextColor(Color.parseColor("#333333"));
        title.setPadding(0, 0, 0, 20);

        // Counter Text
        var textLabel = new TextView(this);
        textLabel.setText("Count: 0");
        textLabel.setTextSize(40f);
        textLabel.setTextColor(Color.parseColor("#007AFF"));
        textLabel.setPadding(0, 0, 0, 50);

        // Button
        var button = new Button(this);
        button.setText("TAP ME");
        button.setBackgroundColor(Color.parseColor("#007AFF"));
        button.setTextColor(Color.WHITE);

        // Logic
        button.setOnClickListener(v -> {{
            counter++;
            textLabel.setText("Count: " + counter);
            if (counter % 10 == 0) {{
                Toast.makeText(this, "Milestone reached: " + counter, Toast.LENGTH_SHORT).show();
            }}
        }});

        // Assemble View
        card.addView(title);
        card.addView(textLabel);
        card.addView(button);
        
        layout.addView(card);

        setContentView(layout);
    }}
}}
"""
    java_file = src_path / "MainActivity.java"
    with open(java_file, "w") as f:
        f.write(java_content)
    print_success("Java source code created.")

    # 7. Build Script (build.sh) - VERSI LEBIH AMAN DAN BERSIH
    build_script = f"""#!/bin/bash
set -e

PROJECT_NAME="{project_name}"
ANDROID_JAR="lib/android.jar"
SRC_DIR="src/main/java"
BIN_DIR="bin"

echo "🚀 Building $PROJECT_NAME..."

# 1. Clean previous build artifacts (Hanya hapus isi folder bin dan file apk)
rm -rf $BIN_DIR/*
rm -f *.apk

# 2. Compile Java
# Output diarahkan ke BIN_DIR agar tidak mengotori source code
echo "☕ Compiling Java..."
javac -cp $ANDROID_JAR -d $BIN_DIR $(find $SRC_DIR -name "*.class" -o -name "*.java")

# 3. Convert to DEX (D8)
echo "🔨 Dexing..."
# --min-api {MIN_SDK} penting agar kompatibel
d8 --lib $ANDROID_JAR --output . --min-api {MIN_SDK} $(find $BIN_DIR -name "*.class")

# 4. Packaging (AAPT2)
echo "📦 Packaging APK..."
aapt2 link -o unaligned.apk -I $ANDROID_JAR --manifest AndroidManifest.xml

# 5. Add classes.dex
echo "🤐 Adding classes.dex..."
zip -uj unaligned.apk classes.dex

# 6. Signing
echo "🔑 Signing APK..."
apksigner sign --ks debug.keystore --ks-pass pass:android --out "$PROJECT_NAME.apk" unaligned.apk

# Cleanup intermediate files
rm -f unaligned.apk classes.dex

echo "✅ BUILD SUCCESS!"
echo "📂 APK Location: $(pwd)/$PROJECT_NAME.apk"
echo "👉 Install: cp $PROJECT_NAME.apk /sdcard/Download/ && echo 'Copied to Download folder'"
"""
    with open("build.sh", "w") as f:
        f.write(build_script)
    
    os.chmod("build.sh", 0o755)
    print_success("build.sh created.")

    print(f"\n{Colors.HEADER}=== DONE ==={Colors.ENDC}")
    print(f"1. cd {project_name}")
    print(f"2. ./build.sh")

if __name__ == "__main__":
    try:
        create_android_project()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(0)
