import argparse
import os
import shutil


def do_configuration():
    os.system('curl https://get.docker.com/ > install_docker.sh')
    os.system('sh install_docker.sh')
    os.system('docker build -t python-env .')


def scan_code(project_path):
    result_path = os.path.abspath(project_path+"/../results")    
    os.system('docker run -v /var/run/docker.sock:/var/run/docker.sock -v '\
        + project_path +':/src horuszup/horusec-cli:latest \
        horusec start -p /src -P '+ project_path +' \
        --output-format sonarqube --log-file-path "/src/horusec-log.log" \
        --json-output-file "/src/horusec-report.json" --information-severity=true')

    
    os.system('docker run --rm -e "WORKSPACE= ${PWD}" -v '+result_path+'/scan-results:/tmp/results -v '+project_path+':/app  shiftleft/scan scan  --src /app -o /tmp/results')

    os.system('docker run -v '+ result_path +':/usr/src/app python-env bandit -r /usr/src/app -f html -o bandit-report.html')
    os.system('docker run -v '+ result_path +':/tmp python-env semgrep --config=p/r2c-ci /usr/src/app --json --output /tmp/semgrep-report.json')


def organise_results(path):
    result_path = os.path.abspath(path+"/../results")
    shutil.move(path+"/horusec-log.log",result_path+"/horusec-log.log")
    shutil.move(path+"/horusec-report.json",result_path+"/horusec-report.json")
    shutil.move(path+"/semgrep-report.json",result_path+"/semgrep-report.json")         
    

parser = argparse.ArgumentParser()
parser.add_argument('--path', help='app path', required=True) 
args = parser.parse_args()
project_path = args.path
print("Project path : "+ project_path)
result_path = os.path.abspath(project_path+"/../results")

do_configuration()
scan_code(project_path)
organise_results(project_path)
print("Please find the results at :"+ result_path)