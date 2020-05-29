import os
import re
import argparse
import subprocess
import sys
import utils
# import scp
import shutil
import db
import pickle

import os


class CmnDriver:

    def update_build(self, file_path, build):
        shutil.copy2("/home/choudhuryd/source/nsx-qe/vdnet/automation/" + file_path, "/tmp/" + file_path)
        f = open("/tmp/" + file_path, 'r')
        filedata = f.read()
        f.close()

        newdata = filedata.replace("BUILD", build)

        f = open("/tmp/" + file_path, 'w')
        f.write(newdata)
        f.close()
        config_file = "/tmp/" + file_path
        return config_file

    def scp_logs(self, log_dir):
        os.chdir("/home/choudhuryd/source/nsx-qe/vdnet/automation")
        # client = scp.Client(host="10.110.233.219", user="root", password="ca$hc0w")
        # client.transfer(logdir, '/var/www/SB/')
        import subprocess
        # sshpass -p "password"
        p = subprocess.Popen(["sshpass", "-p", "ca$hc0w", "scp", "-r", log_dir, "root@10.205.71.79:/var/www/repo/"])
        sts = os.waitpid(p.pid, 0)
        match1 = re.match(".*/(p.*)", log_dir)
        print("\n\n\nTestcase Log Link: http://10.205.71.79:/" + match1.group(1) + "\n\n\n\n")
        return "http://10.205.71.79:/var/www/repo/" + match1.group(1)

    def executor(self, config, testcase, mode=None):
        os.chdir("/home/choudhuryd/source/nsx-qe/vdnet/automation")
        config = config
        testcase = testcase
        execution_list = ['vdnet3/test.py', '--config', config, testcase]
        if mode == "save":
            execution_list.append("--testbed")
            execution_list.append("save")
        if mode == "reuse":
            execution_list.append("--testbed")
            execution_list.append("reuse")

        process = subprocess.Popen(execution_list,
                                   stdout=subprocess.PIPE)
        test_dir = None
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # sys.output.flush()
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
    ap.add_argument("-c", "--config", required=True, help="path to input image")
    ap.add_argument("-t", "--testcase", required=True, help="Testcase file")
    ap.add_argument("-b", "--build", required=False, help="build number")
    ap.add_argument("-m", "--mode", required=False, help="mode")
    args = vars(ap.parse_args())
    print(args)
    obj = CmnDriver()
    if args['mode']:
         mode = args['mode'].split(",")


    pickle_off = open("/home/choudhuryd/build.pickle","rb")
    build = pickle.load(pickle_off)
    print(build)
    pickle_off.close()

    config_file = obj.update_build(args['config'], build["build_number"].rstrip())
    #for mode in mode:
    test_dir = obj.executor(config_file, args['testcase'])

    result_dict = utils.Utils.result_details(test_dir)
    print(build)

    # Copy Logs to Web Server
    log_link = obj.scp_logs(test_dir)

    # Push Data to DB
    build = build["build_number"].rstrip()
    db.Database.insert_db(result_dict,build,log_link)


