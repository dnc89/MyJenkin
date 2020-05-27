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
        shutil.copy2("/home/choudhuryd/source/nsx-qe/vdnet/automation/"+file_path, "/tmp/"+file_path)
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
        os.chdir("/home/choudhuryd/")
        os.chdir("/home/choudhuryd/source/nsx-qe/vdnet/automation")
       # client = scp.Client(host="10.205.71.79", user="root", password="ca$hc0w")
       # client.transfer(logdir, '/var/www/SB/')
        import subprocess
        #sshpass -p "password"
        p = subprocess.Popen(["sshpass", "-p", "ca$hc0w", "scp", "-r", log_dir, "root@10.205.71.79:/var/www/repo/"])
        sts = os.waitpid(p.pid, 0)
        match1 = re.match(".*/(p.*)",log_dir)
        print ("\n\n\nTestcase Log Link: http://10.205.71.79/"+match1.group(1)+"\n\n\n\n")
        return "http://10.205.71.79/"+match1.group(1)



    def executor(self,config,testcase):
        os.chdir("/home/choudhuryd/source/nsx-qe/vdnet/automation")
        config = config
        testcase = testcase

        process = subprocess.Popen(['vdnet3/test.py', '--config', config, testcase], stdout=subprocess.PIPE)
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
    args = vars(ap.parse_args())
    print (args)
    obj = Driver()
    rc = obj.update_build(args['config'],args['build'])
    test_dir = obj.executor(rc,args['testcase'])
    #test_dir = "/tmp/pytest-of-choudhuryd/pytest-20/"

    ##Find Result Dictionary##

    result_dict = utils.Utils.result_details(test_dir)
    print (test_dir)

    #Copy Logs to Web Server
    log_link = obj.scp_logs(test_dir)

    #Push Data to DB
    db.Database.insert_db(result_dict,args['build'],log_link)
