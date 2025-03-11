"""
Module dependency check script
"""
import sys
print(f"Python version: {sys.version}")

modules = [
    "dash", 
    "dash_bootstrap_components", 
    "dash_core_components", 
    "dash_html_components", 
    "dash_table", 
    "flask", 
    "gunicorn", 
    "lxml", 
    "numpy", 
    "pandas", 
    "pyld", 
    "pyreadstat", 
    "rdflib"
]

failed = False
for module in modules:
    try:
        __import__(module)
        print(f"✓ {module} imported successfully")
    except ImportError as e:
        failed = True
        print(f"✗ Failed to import {module}: {e}")

if failed:
    print("\n❌ Some modules failed to import")
    sys.exit(1)
else:
    print("\n✅ All modules imported successfully")
    
# Check if app.server can be imported
try:
    from app import server
    print("✓ app.server imported successfully")
except Exception as e:
    print(f"✗ Failed to import app.server: {e}")
    sys.exit(1)

print("\n✅ Application ready to serve") 