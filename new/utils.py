import re


class Utils():

    def result_details(log_dir):
        started = False
        log_path = log_dir + "/session.log"
        collected_lines = []
        with open(log_path, "r") as fp:
            for i, line in enumerate(fp.readlines()):
                if "Test summary:" in line or started == True:
                    started = True
                    # print ( "started at line", i )# counts from zero !
                    collected_lines.append(line.rstrip())
                continue
        # print (collected_lines)
        print(collected_lines)
        result_dict = {}
        '''
        lookup = 'Test summary'
        line_number = 0
        with open(filename) as myFile:
            for num, line in enumerate(myFile, 1):
                if lookup in line:
                    print('found at line:', num)
                    line_number = num
                    break
        myFile.close()


        fileHandle = open ( 'test3.txt',"r" )
        lineList = fileHandle.readlines()
        fileHandle.close()
        print lineList
        print "The last line is:"
        print lineList[len(lineList)-1]
        lines=[line_number+1, len(lineList)]
        i=0
        f=open('filename')
        for line in f:
            if i in lines:
                print i
            i+=1
        '''
        for element in collected_lines:
            find = re.match("\|.* (\w+) .*\|.* (\w+).*\| .* (/.*/\w+) .*", element)
            if find:
                result_dict[find.group(1)] = find.group(2)

        print("\n\nResult of Testcases")
        print(result_dict)
        return result_dict
