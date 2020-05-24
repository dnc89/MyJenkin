
import re
import argparse
import subprocess
import datetime
import shutil
import os
import sys
# import utils
# import scp
import shutil
# import db

import os


class Driver:

    def scp_logs(self, log_dir):

        date = datetime.datetime.today()
        date = str(date)
        date = date.replace(" ", "_")
        destination = "/var/www/repo/spark_logs/"+date
        try:
            create_dir = subprocess.Popen(["sshpass", "-p", "ca$hc0w", "ssh", "root@10.205.71.79",
                                           "mkdir", "777", destination])
            sts = os.waitpid(create_dir.pid, 0)
            print("Try executed")
        except Exception as e:
            print("on exception")
            print(e)

        p = subprocess.Popen(["sshpass", "-p", "ca$hc0w", "scp", "-r", log_dir, "root@10.205.71.79:/var/www/repo"])
        sts = os.waitpid(p.pid, 0)
        #match1 = re.match(".*/(p.*)", log_dir)
        #print("\n\n\nTestcase Log Link: http://10.205.71.79/" + match1.group(1) + "\n\n\n\n")
        print("\n\n\nTestcase Log Link: http://10.205.71.79/"+"spark_logs/"+date + "\n\n\n\n")
        #return "http://10.110.233.219/SB/" + match1.group(1)

    def executor(self, build_number, branch, physical_config, logical_config, tests):
        os.chdir("/home/choudhuryd/")
        os.chdir("/home/choudhuryd/code/nsx-qe/spark/")

        args_list = ["./test.py", "--parent-build", build_number, "--branch",
                     branch, "--", "--config", physical_config, "--vdtopology-out", "jen.pk3",
                     "--vdtestbed-out", "jen.pkl", "--logical-config", logical_config, ]
        for test in tests:
            args_list.append(test)

        params_list = ["--service-config-path", "config/fvt/service_automation/", "--cachetestbed", "1"]

        for test in params_list:
            args_list.append(test)

        print("List of parameters found for cli", args_list)
        process = subprocess.Popen(args_list, stdout=subprocess.PIPE)
        test_dir = None
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.decode('utf-8'))
                end = output.decode('utf-8')
                if re.match("Test session directory: (.*)", end):
                    dir = re.match("Test session directory: (.*)", end)
                    test_dir = dir.group(1)
                if re.match("^=.* seconds.*", end):
                    return test_dir
        rc = process.poll()
        return rc


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-l", "--logical_config", required=True, help="Logical config file")
    ap.add_argument("-c", "--physical_config", required=True, help="Physical config file")
    ap.add_argument("-b", "--build_number", required=False, help="build number")
    ap.add_argument("-p", "--product", required=False, help="Product info")
    ap.add_argument("-br", "--branch", required=False, help="branch info")
    ap.add_argument("-t", "--tests", required=False, help="testcase files")

    args = vars(ap.parse_args())
    print(args)
    obj = Driver()
    tests = args["tests"].split(",")
    print(tests)
    test_dir = obj.executor(args["build_number"], args["branch"], args["physical_config"],
                            args["logical_config"], tests)
    print(test_dir)
