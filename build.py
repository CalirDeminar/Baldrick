import subprocess
import shutil
import os

if __name__ == '__main__':
    if os.path.exists('./dist/baldrick'):
        shutil.rmtree('./dist/baldrick')
    if os.path.exists('./dist/baldrick.zip'):
        os.remove('./dist/baldrick.zip')
    subprocess.call(r"PyInstaller baldrick.spec")
    os.mkdir('./dist/baldrick/routes')
    shutil.copy('./routes/example.csv', './dist/baldrick/routes/example.csv')
    shutil.copy('./config.json', './dist/baldrick/config.json')
    shutil.make_archive("./dist/baldrick", "zip", "./dist/baldrick")
