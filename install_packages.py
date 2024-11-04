import subprocess


with open("requirements.txt") as f:
    packages = f.readlines()


packages = [pkg.strip() for pkg in packages if pkg.strip()]


with open("errors_requirements.txt", "w") as error_file:
    error_file.write("")


for package in packages:
    try:
        print(f"Installing {package}...")
        subprocess.check_call(["pip", "install", "--no-deps", package])
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")
        # Запишите ошибочный пакет в errors_requirements.txt
        with open("errors_requirements.txt", "a") as error_file:
            error_file.write(f"{package}\n")

print("Installation completed. Check errors_requirements.txt for any failed packages.")