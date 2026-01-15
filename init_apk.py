import os
import sys
import subprocess
import urllib.request
import time

# Warna warni
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, color=Colors.BLUE):
    print(f"{color}[*] {message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}[+] {message}{Colors.ENDC}")

def download_file(url, filename):
    try:
        print_status(f"Download {filename}...")
        urllib.request.urlretrieve(url, filename)
        print_success("Download complete.")
    except Exception as e:
        print(f"{Colors.FAIL}Download failed.: {e}{Colors.ENDC}")
        sys.exit(1)

def create_android_project():
    print(f"{Colors.HEADER}{Colors.BOLD}=== Project Init Android Termux ==={Colors.ENDC}")
    
    # 1. Input User
    project_name = input(f"{Colors.BOLD}Project Folder Name (without space): {Colors.ENDC}").strip()
    if not project_name:
        print("The project name cannot be empty.")
        return

    package_name = input(f"{Colors.BOLD}Package Name (ex: com.saya.app): {Colors.ENDC}").strip()
    if not package_name:
        package_name = "com.demo.app"
    
    # 2. Anuin folder
    if os.path.exists(project_name):
        print(f"{Colors.WARNING}Folder '{project_name}' sudah ada!{Colors.ENDC}")
        confirm = input("Continue? (y/n): ")
        if confirm.lower() != 'y':
            return
    else:
        os.makedirs(project_name)
    
    os.chdir(project_name)
    print_success(f"Masuk ke folder {project_name}")

    # 3. Download android.jar
    if not os.path.exists("android.jar"):
        url = "https://github.com/Sable/android-platforms/raw/master/android-34/android.jar"
        download_file(url, "android.jar")
    
    # 4. Buat Keystore Otomatis
    if not os.path.exists("debug.keystore"):
        print_status("Membuat Keystore (Password: 123456)...")
        cmd = [
            "keytool", "-genkey", "-v", 
            "-keystore", "debug.keystore", 
            "-storepass", "123456", 
            "-alias", "androiddebugkey", 
            "-keypass", "123456", 
            "-keyalg", "RSA", 
            "-keysize", "2048", 
            "-validity", "10000",
            "-dname", "CN=Android Debug,O=Android,C=US"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success("Keystore created successfully.")

    # 5. Anuin Struktur Folder Java
    package_path = package_name.replace('.', '/')
    os.makedirs(package_path, exist_ok=True)

    # 6. Anuin AndroidManifest.xml
    manifest_content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">

    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="34" />

    <application android:label="{project_name}" android:theme="@android:style/Theme.DeviceDefault.Light">
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
    print_success("AndroidManifest.xml dibuat.")

    # 7. Buat MainActivity.java (Modern Java 17)
    java_content = f"""package {package_name};

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Button;
import android.widget.Toast;
import android.view.Gravity;
import android.graphics.Color;

public class MainActivity extends Activity {{
    
    private int counter = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        // Layout Utama
        var layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        layout.setBackgroundColor(Color.WHITE);

        // Teks Counter
        var textLabel = new TextView(this);
        textLabel.setText("Hello Termux!");
        textLabel.setTextSize(30f);
        textLabel.setTextColor(Color.BLACK);
        textLabel.setGravity(Gravity.CENTER);
        textLabel.setPadding(0, 0, 0, 50);

        // Tombol
        var button = new Button(this);
        button.setText("Klik Saya");

        // Event Listener (Lambda Java 8+)
        button.setOnClickListener(v -> {{
            counter++;
            textLabel.setText("Hitungan: " + counter);
            
            if (counter % 5 == 0) {{
                Toast.makeText(this, "Wow! Sudah " + counter, Toast.LENGTH_SHORT).show();
            }}
        }});

        layout.addView(textLabel);
        layout.addView(button);

        setContentView(layout);
    }}
}}
"""
    with open(f"{package_path}/MainActivity.java", "w") as f:
        f.write(java_content)
    print_success(f"MainActivity.java dibuat di {package_path}")

    # 8. Buat Script Build (build.sh)
    build_script = f"""#!/bin/bash
set -e # Stop jika ada error

echo "🚀 Start Build Project: {project_name}..."

# Bersihkan file lama
rm -f classes.dex app.apk app-signed.apk
rm -rf com # Hapus folder compile lama (opsional, hati-hati jika source code campur)

echo "☕ Compiling Java (Javac)..."
# Compile semua file java di dalam folder package
javac -cp android.jar -d . {package_path}/*.java

echo "🔨 Dexing (D8)..."
# Menggunakan D8 untuk convert ke DEX (Support Java 17 features)
d8 --lib android.jar --output . --min-api 21 $(find . -name "*.class")

echo "📦 Packaging (AAPT2)..."
aapt2 link -o app.apk -I android.jar --manifest AndroidManifest.xml

echo "🤐 Zipping classes.dex..."
zip -u app.apk classes.dex

echo "🔑 Signing APK..."
apksigner sign --ks debug.keystore --ks-pass pass:123456 --out {project_name}.apk app.apk

echo "✅ SELESAI! File APK: {project_name}.apk"
echo "👉 Install: cp {project_name}.apk /sdcard/Download/"
"""
    with open("build.sh", "w") as f:
        f.write(build_script)
    
    # Bikin executable
    os.chmod("build.sh", 0o755)
    print_success("build.sh dibuat dan siap dijalankan.")

    print(f"\n{Colors.HEADER}Project Siap!{Colors.ENDC}")
    print(f"Ketik perintah berikut untuk mem-build aplikasi:")
    print(f"{Colors.BOLD}cd {project_name}{Colors.ENDC}")
    print(f"{Colors.BOLD}./build.sh{Colors.ENDC}")

if __name__ == "__main__":
    try:
        create_android_project()
    except KeyboardInterrupt:
        print("\nDibatalkan.")
