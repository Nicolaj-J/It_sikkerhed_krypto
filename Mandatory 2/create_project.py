import platform
import os


cwd = os.getcwd()
project_name = input("Write the name of the project: ")
operating_system = platform.system()
readme_txt = f"""
# {project_name}
    What is the project about...

## Installation
    How do you install it

## Usage
    How do you use it

## Contributing
    Who made it

## License
    Are there a license?

"""

install_txt = f"""
Activate the venv:
    From project folder:
        {project_name}_venv\\Scripts\\activate
    Parent folder:
        {project_name}\\{project_name}_venv\\Scripts\\activate
    
Install and usage of Pycodestyle:
    Pycodestyle is used to help with pep8 implementation into python scripts and programs. Write the command and all
    places that doesnt follow pep8 will be listed in the terminal.

    Installation:
        pip install pycodestyle
    
    Usage:
        Write this in cmd:
            Pycodestyle this_file.py

Install and usage of pipreqs
    pipreqs is used to make requirements.txt files. These files makes it easier to get the required libraries and dependicies
    for a program or a script.

    Installation:
        pip install pipreqs
    
    Usage:
        Write this in cmd while being in the projectfolder:
            pipreqs {{project_name}}

        To install the the requirements.txt
            pip install -r requirements.txt
    
"""

requirement_txt = """
pycodestyle
pipreqs
"""

match operating_system:
    case "Linux":
        try:
            import virtualenv
        except ImportError:
            os.system("pip install virtualenv")
        os.system(f"virtualenv {project_name}_env")
        f= open(f"{project_name}\\README.txt","w+")
        f.write(readme_txt)
        f.close()
        f= open(f"{project_name}\\requirements.txt","w+")
        f.write(readme_txt)
        f.close()

    case "Windows":
        try:
            import virtualenv
        except ImportError:
            os.system("pip install virtualenv")
        os.system(f"mkdir {project_name}")
        os.system(f"virtualenv {project_name}\\{project_name}_venv")
        f= open(f"{project_name}\\README.txt","w+")
        f.write(readme_txt)
        f.close()
        f= open(f"{project_name}\\requirements.txt","w+")
        f.write(requirement_txt)
        f.close()
        f= open(f"{project_name}\\install_txt","w+")
        f.write(install_txt)
        f.close()
            
    case "Darwin":
        print("Your os is not supported yet")
