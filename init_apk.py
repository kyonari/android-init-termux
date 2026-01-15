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
    tools = ["javac", "d8", "aapt2", "apksigner", "keytool", "zip"]
    missing = []
    print_status("Checking dependencies...")
    for tool in tools:
        if not shutil.which(tool):
            missing.append(tool)
    
    if missing:
        print_error(f"Tool tidak ditemukan: {', '.join(missing)}")
        print(f"{Colors.WARNING}Install paket: pkg install openjdk-17 android-tools{Colors.ENDC}")
        sys.exit(1)
    print_success("Dependencies OK.")

def download_file_with_progress(url, filename):
    try:
        print_status(f"Downloading {filename}...")
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\r{Colors.CYAN}Progress: [{('=' * (percent // 5)).ljust(20)}] {percent}%{Colors.ENDC}")
                sys.stdout.flush()
        urllib.request.urlretrieve(url, filename, reporthook)
        print()
        print_success("Download complete.")
    except Exception as e:
        print_error(f"Download failed: {e}")
        sys.exit(1)

def create_android_project():
    print(f"{Colors.HEADER}{Colors.BOLD}=== Android Project Generator (Java 17) ==={Colors.ENDC}")
    
    check_dependencies()

    # 1. Input User
    default_name = "MyJava17App"
    proj_input = input(f"{Colors.BOLD}Project Name (default: {default_name}): {Colors.ENDC}").strip()
    project_name = proj_input if proj_input else default_name
    project_name = "".join(x for x in project_name if x.isalnum() or x in "_-")

    default_pkg = "com.java17.app"
    pkg_input = input(f"{Colors.BOLD}Package Name (default: {default_pkg}): {Colors.ENDC}").strip()
    package_name = pkg_input if pkg_input else default_pkg

    # 2. Setup Folder
    project_path = Path(project_name)
    if project_path.exists():
        print(f"{Colors.WARNING}Folder '{project_name}' sudah ada!{Colors.ENDC}")
        if input("Overwrite? (y/n): ").lower() != 'y': return
    else:
        project_path.mkdir()

    os.chdir(project_path)
    
    src_path = Path("src/main/java") / package_name.replace('.', '/')
    src_path.mkdir(parents=True, exist_ok=True)
    Path("bin").mkdir(exist_ok=True)
    Path("lib").mkdir(exist_ok=True)

    # 3. Download android.jar
    android_jar_path = Path("lib/android.jar")
    if not android_jar_path.exists():
        download_file_with_progress(ANDROID_JAR_URL, str(android_jar_path))
    
    # 4. Keystore
    if not os.path.exists("debug.keystore"):
        cmd = [
            "keytool", "-genkey", "-v", "-keystore", "debug.keystore", 
            "-storepass", "android", "-alias", "androiddebugkey", 
            "-keypass", "android", "-keyalg", "RSA", "-keysize", "2048", 
            "-validity", "10000", "-dname", "CN=Android Debug,O=Android,C=US"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Manifest
    manifest_content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">
    <uses-sdk android:minSdkVersion="{MIN_SDK}" android:targetSdkVersion="{TARGET_SDK}" />
    <application android:label="{project_name}" android:theme="@android:style/Theme.DeviceDefault.Light">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
    with open("AndroidManifest.xml", "w") as f: f.write(manifest_content)

    # 6. MainActivity.java (Java 17 Style with 'var')
    java_content = f"""package {package_name};

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Button;
import android.widget.Toast;
import android.view.Gravity;
import android.graphics.Color;
import java.time.LocalTime; // Contoh API Java modern

public class MainActivity extends Activity {{
    
    private int counter = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        // Layout Container (Menggunakan 'var' Java 10+)
        var layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        layout.setBackgroundColor(Color.parseColor("#E0F7FA")); // Light Cyan

        // Text
        var textLabel = new TextView(this);
        textLabel.setText("Java 17 on Termux");
        textLabel.setTextSize(28f);
        textLabel.setTextColor(Color.parseColor("#006064"));
        textLabel.setGravity(Gravity.CENTER);
        textLabel.setPadding(0, 0, 0, 50);

        // Button
        var button = new Button(this);
        button.setText("TAP HERE");
        button.setBackgroundColor(Color.parseColor("#0097A7"));
        button.setTextColor(Color.WHITE);

        // Logic
        button.setOnClickListener(v -> {{
            counter++;
            // Contoh format string Java modern
            var message = "Count: %d".formatted(counter);
            textLabel.setText(message);
            
            if (counter % 5 == 0) {{
                Toast.makeText(this, "Milestone! " + counter, Toast.LENGTH_SHORT).show();
            }}
        }});

        layout.addView(textLabel);
        layout.addView(button);
        setContentView(layout);
    }}
}}
"""
    with open(src_path / "MainActivity.java", "w") as f: f.write(java_content)

    # 7. Build Script (Target Java 17)
    build_script = f"""#!/bin/bash
set -e
PROJECT_NAME="{project_name}"
ANDROID_JAR="lib/android.jar"
SRC_DIR="src/main/java"
BIN_DIR="bin"

echo "🚀 Building $PROJECT_NAME (Java 17 Mode)..."

rm -rf $BIN_DIR/* *.apk

echo "☕ Compiling Java 17..."
# Menggunakan flag -source 17 -target 17
# Ini menghasilkan bytecode versi 61 yang masih didukung d8 terbaru
javac -source 17 -target 17 -cp $ANDROID_JAR -d $BIN_DIR $(find $SRC_DIR -name "*.java")

echo "🔨 Dexing..."
# d8 akan memproses bytecode Java 17
d8 --lib $ANDROID_JAR --output . --min-api {MIN_SDK} $(find $BIN_DIR -name "*.class")

echo "📦 Packaging..."
aapt2 link -o unaligned.apk -I $ANDROID_JAR --manifest AndroidManifest.xml
zip -uj unaligned.apk classes.dex

echo "🔑 Signing..."
apksigner sign --ks debug.keystore --ks-pass pass:android --out "$PROJECT_NAME.apk" unaligned.apk

rm -f unaligned.apk classes.dex
echo "✅ SUCCESS: $(pwd)/$PROJECT_NAME.apk"
"""
    with open("build.sh", "w") as f: f.write(build_script)
    os.chmod("build.sh", 0o755)

    print_success("Project created with Java 17 configuration.")
    print(f"cd {project_name} && ./build.sh")

if __name__ == "__main__":
    create_android_project()
