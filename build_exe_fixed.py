"""
Build script for SFDA Dashboard (No Export Features)
"""

import PyInstaller.__main__
import os
import shutil

print("="*60)
print("🔨 Building SFDA Dashboard Executable")
print("📌 Export features removed")
print("="*60)

# Clean previous builds
for folder in ['dist', 'build']:
    if os.path.exists(folder):
        shutil.rmtree(folder)

# Check if Excel file exists
if not os.path.exists('sfda_products.xlsx'):
    print("❌ ERROR: sfda_products.xlsx not found!")
    print("Please place your Excel file in this folder before building.")
    input("\nPress Enter to exit...")
    exit(1)

# PyInstaller arguments
args = [
    'sfda_complete.py',  # Save the updated file with this name
    '--onefile',
    '--name=SFDA_Database_Search',
    '--console',
    '--add-data=sfda_products.xlsx;.',
    '--clean',
    '--noconfirm'
]

print("\n📦 Building executable...")
PyInstaller.__main__.run(args)

print("\n" + "="*60)
print("✅ Build Complete!")
print("📁 Executable location: dist/SFDA_Database_Search.exe")
print("="*60)

# Copy Excel file to dist folder
shutil.copy2('sfda_products.xlsx', 'dist/sfda_products.xlsx')
print("✅ Excel file copied to dist folder")

print("\n📋 Features Removed:")
print("   ❌ Excel Export")
print("   ❌ CSV Export")
print("   ❌ PDF Export")
print("\n✅ Features Kept:")
print("   ✓ Search by any field")
print("   ✓ Advanced filters")
print("   ✓ Statistics dashboard")
print("   ✓ Network sharing")
print("   ✓ Pagination")

print("\n📋 To run:")
print("1. Go to the 'dist' folder")
print("2. Double-click SFDA_Database_Search.exe")
print("="*60)

input("\nPress Enter to exit...")