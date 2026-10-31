#!/usr/bin/env python3
import os
import re

def audit_env_and_secrets():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_example_path = os.path.join(base_dir, ".env.example")
    
    # Read .env.example
    env_vars = set()
    with open(env_example_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=")[0].strip()
                env_vars.add(key)
                
    print(f".env.example defines {len(env_vars)} variables: {sorted(env_vars)}")
    
    # Search python code for os.environ, os.getenv, settings
    code_vars = set()
    hardcoded_secrets = []
    
    for root, dirs, files in os.walk(os.path.join(base_dir, "backend")):
        dirs[:] = [d for d in dirs if d not in (".venv", "__pycache__", ".pytest_cache")]
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as py_file:
                    content = py_file.read()
                    
                    # os.getenv / os.environ
                    for match in re.findall(r'os\.getenv\(["\']([A-Z0-9_]+)["\']', content):
                        code_vars.add(match)
                    for match in re.findall(r'os\.environ\.get\(["\']([A-Z0-9_]+)["\']', content):
                        code_vars.add(match)
                    for match in re.findall(r'os\.environ\[["\']([A-Z0-9_]+)["\']\]', content):
                        code_vars.add(match)
                        
                    # Settings class fields
                    if "config.py" in f:
                        for line in content.splitlines():
                            line = line.strip()
                            if line and not line.startswith("#") and ":" in line and "=" in line:
                                field = line.split(":")[0].strip()
                                if field.isupper():
                                    code_vars.add(field)

    print(f"Backend code defines/reads {len(code_vars)} config variables: {sorted(code_vars)}")
    
    missing_in_example = code_vars - env_vars
    unused_in_example = env_vars - code_vars
    
    print(f"\nVariables in code but missing from .env.example ({len(missing_in_example)}): {sorted(missing_in_example)}")
    print(f"Variables in .env.example but not in backend Settings ({len(unused_in_example)}): {sorted(unused_in_example)}")

if __name__ == "__main__":
    audit_env_and_secrets()
