import subprocess
import re
import pickle
import argparse


class GetBuild():
    def get_build(self, product, branch):
        out = subprocess.Popen(
            ['/build/apps/bin/bld', '-k', 'ob', 'show', '-b', branch, '-p',
             product, '-t', 'release',
             '-s', 'succeeded', '-c', '1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        stdout, stderr = out.communicate()
        stdout = stdout.split("\n")
        print("Build Details : ",stdout)
        build = {}
        for var in stdout:
            if var.startswith("ob-"):
                build = re.findall(r"\d+ ", var)
                # product = re.findall(r"nsx-\w+",var)
                print(build[0])
                print(product)
                build['build_number'] = build[0]
                print("Latest Stable Build Found is : ", build[0])
        with open('/home/code/build.pickle', 'wb') as f:
            pickle.dump(build, f)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--product", required=True, help="product name")
    ap.add_argument("-b", "--branch", required=True, help="branch name")
    args = vars(ap.parse_args())
    print(args)
    obj = GetBuild()
    rc = obj.get_build(args['product'], args['branch'])


