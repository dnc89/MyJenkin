import os
import re
import argparse
import subprocess
import sys
import utils
#import scp
import shutil
import db

import os

class Driver:



    def update_build(self,file_path,build):
        shutil.copy2("/home/code/nsx-qe/vdnet/automation/"+file_path, "/tmp/"+file_path)
        f = open("/tmp/"+file_path,'r')
        filedata = f.read()
        f.close()
        
        newdata = filedata.replace("BUILD", build)
        
        f = open("/tmp/"+file_path,'w')
        f.write(newdata)
        f.close()
        config_file = "/tmp/"+file_path
        return config_file

    def scp_logs(self,log_dir):
        os.chdir("/home/code/")
        os.chdir("/home/code/nsx-qe/vdnet/automation")
       # client = scp.Client(host="10.110.233.219", user="root", password="ca$hc0w")
       # client.transfer(logdir, '/var/www/SB/')
        import subprocess
        #sshpass -p "password"
        p = subprocess.Popen(["sshpass", "-p", "ca$hc0w", "scp", "-r", log_dir, "root@10.110.235.235:/var/www/repo/"])
        sts = os.waitpid(p.pid, 0)
        match1 = re.match(".*/(p.*)",log_dir)
        print ("\n\n\nTestcase Log Link: http://10.110.235.235:/"+match1.group(1)+"\n\n\n\n")
        return "http://10.110.235.235:/var/www/repo/"+match1.group(1)



    def executor(self,config,testcase,mode):
        os.chdir("/home/code/")
        os.chdir("/home/code/nsx-qe/vdnet/automation")
        config = config
        testcase = testcase
        mode = mode

        process = subprocess.Popen(['vdnet3/test.py', '--config', config, testcase, "--testbed", mode], stdout=subprocess.PIPE)
        test_dir = None
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                #sys.output.flush()
                print (output.decode('utf-8'))
                end = output.decode('utf-8')
                if re.match("Test session directory: (.*)", end):
                    dir = re.match("Test session directory: (.*)", end)
                    test_dir = dir.group(1)
                if re.match("^=.* seconds.*", end):
                    return test_dir
        rc = process.poll()
        return rc
        
#        #subprocess.call(["git","pull","--rebase"])
#        result = subprocess.run(['vdnet3/test.py', '--config', 'L2vpn_Edge.yaml', 'TDS/NSXTransformers/Edge/L2VPN/L2vpn_AutoEdge/L2vpn_AutoEdgeTds.yaml::L2vpn_Setup', '--use-product-sdks', '--testbed', 'save'], stdout=subprocess.PIPE)
#        print (result.stdout.decode('utf-8'))
#    
#    p = subprocess.Popen(['vdnet3/test.py', '--config', 'L2vpn_Edge.yaml', 'TDS/NSXTransformers/Edge/L2VPN/L2vpn_AutoEdge/L2vpn_AutoEdgeTds.yaml::L2vpn_Setup', '--use-product-sdks', '--testbed', 'save'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    for line in p.stdout.readlines():
#        print (line.decode('utf-8'))


if __name__== "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", required=True, help="path to input image")
    ap.add_argument("-t", "--testcase", required=True, help="Testcase file")
    ap.add_argument("-b", "--build", required=False, help="build number")
    ap.add_argument("-m", "--mode", required=False, help="mode")
    args = vars(ap.parse_args())
    print (args)
    obj = Driver()
    mode = args['mode'].split(",")
    rc = obj.update_build(args['config'],args['build'])
    for mode in mode:
        test_dir = obj.executor(rc,args['testcase'],mode)
    #test_dir = "/tmp/pytest-of-choudhuryd/pytest-20/"

    ##Find Result Dictionary##

    result_dict = utils.Utils.result_details(test_dir)
    print (test_dir)

    #Copy Logs to Web Server
    log_link = obj.scp_logs(test_dir)

   # passed_count = 0
   # for test in result_dict:
   #     if result_dict[test] == "PASS":
   #         passed_count = passed_count+1

   # #Push Data to DB
   # print ("Total passed:",passed_count)
   # if passed_count > 4:
   #     db.Database.insert_db(result_dict,args['build'],log_link)
