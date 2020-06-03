import urllib.request
import re
import json
from prettytable import PrettyTable
import prettytable
from datetime import date


def func_analysis(result_link, jenkins_link):
    test_link = result_link
    cases = urllib.request.urlopen(test_link)
    case_data = json.loads(cases.read())

    table = PrettyTable()
    table.hrules = prettytable.ALL
    table.field_names = ["TC-No", "Testcase", "Result", "Logs", "Analysis", "Action_Bundle_Detail"]
    result = {}
    number_test = {}
    number_test["Total"] = 0
    number_test["Pass_Case"] = 0
    number_test["Fail_Case"] = 0
    case_number = 0
    today = date.today()
    datefrmt = today.strftime("%B_%d")
    for links in case_data:
        case_number += 1
        number_test["Total"] += 1
        test = str(links['testname'].split("::")[-1])
        if test == "test_create_base_topo":
            web = urllib.request.urlopen(str(links['info']).split(">")[0].split("=")[1].replace("/tmp/pytest-of-choudhuryd",
                                                                                                jenkins_link).replace(
                '"', ''))
            data = (web.read()).decode("utf-8")
            build = re.findall("Using.*([\d]{8})\s*for validation", data)
            suite_regex = re.findall("file_or_dir.*fvt.*\.py", data)
            suite_name = (suite_regex[0].split(",")[-1]).split("/")[-2].upper()
        if links["result"] == 0:
            number_test["Pass_Case"] += 1
            row1 = [case_number, test, "PASS",
                    (str(links['info']).split(">")[0].split("=")[1].replace("/tmp/pytest-of-choudhuryd",
                                                                            jenkins_link)).replace(
                        '"', ''), "NA", "NA"]
            result[test] = "PASS"
        else:
            number_test["Fail_Case"] += 1
            row1 = [case_number, test, "FAIL",
                    (str(links['info']).split(">")[0].split("=")[1].replace("/tmp/pytest-of-choudhuryd",
                                                                            jenkins_link)).replace(
                        '"', '')]
            result[test] = "FAIL"
            web = urllib.request.urlopen(str(links['info']).split(">")[0].split("=")[1].replace("/tmp/pytest-of-choudhuryd",
                                                                                                jenkins_link).replace(
                '"', ''))
            data = (web.read()).decode("utf-8")
            failure = re.findall(">\s{4,}.*\n.*\n.*tests.*\d+", data)
            if failure:
                for case in failure:
                    if re.search("verify_datapath|verify_cli", case):
                        fail_text = "Failure in Action Bundle:- %s %s" % ("\n",case.split(")")[0].split('>')[1].lstrip())
                        file_text = "File and Line of Failure:-  %s %s" % ("\n", case.split(")")[1].split("\n")[2])
                        final_text = fail_text + "\n\n" + file_text
                        action_bundle_line = set()
                        if re.search("\d.*(primary_act|verify_act|post_act|pre_act).*Fail.*\|", data):
                            res = ""
                            for action in re.findall("\d.*(primary_act|verify_act|post_act|pre_act).*Fail.*\|", data):
                                # TODO: Extract Failure from the Action Bundle and write  it down in res
                                res = res + action + "\n"
                                for action_ver in re.findall("\d.*" + action + ".*Fail.*\|", data):
                                    action_bundle_line.add(int(action_ver.split("|")[0].strip()))
                                    # for number in action_bundle_line:
                                    #    print("The line Number for action bundle is ", number)
                                    #    pattern=r'str(number)+r".*\|.*Fail(.|\n)*\|(\s)*Fail \|(.|\n)"'
                                    #    bundle_text = re.findall(pattern,data)
                                    #    print(str(number)+r".*\|.*Fail(.|\n)*\|(\s)*Fail \|(.|\n)")
                                    #    print(bundle_text)
                        elif re.search("\d.*(primary_act|verify_act|post_act|pre_act).*Error.*\|", data):
                            res = ""
                            for action in re.findall("\d.*(primary_act|verify_act|post_act|pre_act).*Error.*\|", data):
                                # TODO: Extract Failure from the Action Bundle and write  it down in res
                                res = res + action + "\n"
                                for action_ver in re.findall("\d.*" + action + ".*Error.*\|", data):
                                    action_bundle_line.add(int(action_ver.split("|")[0].strip()))
                                    # for number in action_bundle_line:
                                    #    print("The line Number for action bundle is ", number)
                                    #    pattern=r'str(number)+r".*\|.*Fail(.|\n)*\|(\s)*Fail \|(.|\n)"'
                                    #    bundle_text = re.findall(pattern,data)
                                    #    print(str(number) +r".*\|.*Error(.|\n)*\|(\s)*Fail \|(.|\n)")
                                    #    print(bundle_text)
                        row1.append(final_text)
                        row1.append(action_bundle_line)
                    elif re.search("obj|delete|create|put|get|verify", case):
                        #fail_text = "Failure in API Call:-  %s" % case.split("../")[0].split('>')[1].lstrip()
                        #file_text = "File and Line of Failure:-  %s" % case.split("../")[-1]
                        final_text = "Failure in API Call :- %s" % case
                        #final_text = fail_text + file_text
                        row1.append(final_text)
                        row1.append("NA")
                        break
                    elif re.search("exclude", case):
                        fail_text = "Failure in Action Bundle:- %s %s" % ("\n",case.split(")")[0].split('>')[1].lstrip())
                        file_text = "File and Line of Failure:-  %s %s" % ("\n", case.split(")")[1].split("\n")[2])
                        final_text = fail_text + file_text
                        action_bundle_line = set()
                        if re.search("\d.*(primary_act|verify_act|post_act|pre_act).*Fail.*\|", data):
                            res = ""
                            for action in re.findall("\d.*(primary_act|verify_act|post_act|pre_act).*Fail.*\|", data):
                                # TODO: Extract Failure from the Action Bundle and write  it down in res
                                res = res + action + "\n"
                                for action_ver in re.findall("\d.*" + action + ".*Fail", data):
                                    action_bundle_line.add(int(action_ver.split("|")[0].strip()))
                                    # for number in action_bundle_line:
                                    #    print("The line Number for action bundle is ", number)
                                    #    pattern=r'str(number)+r".*\|.*Fail(.|\n)*\|(\s)*Fail \|(.|\n)"'
                                    #    bundle_text = re.findall(pattern,data)
                                    #    print(str(number) + ".*\|.*Fail(.|\\n)*\|(\s)*Fail \|(.|\\n)")
                                    #    print(bundle_text)
                        elif re.search("\d.*(primary_act|verify_act|post_act|pre_act).*Error.*\|", data):
                            res = ""
                            for action in re.findall("\d.*(primary_act|verify_act|post_act|pre_act).*Error.*\|", data):
                                # TODO: Extract Failure from the Action Bundle and write  it down in resl
                                res = res + action + "\n"
                                for action_ver in re.findall("\d.*" + action + ".*Error.*\|", data):
                                    action_bundle_line.add(int(action_ver.split("|")[0].strip()))
                                    # for number in action_bundle_line:
                                    #    print("The line Number for action bundle is ", number)
                                    #    pattern=r'str(number)+r".*\|.*Fail(.|\n)*\|(\s)*Fail \|(.|\n)"'
                                    #    bundle_text = re.findall(pattern,data)
                                    #    print(str(number) + r".*\|.*Fail(.|\n)*\|(\s)*Fail \|(.|\n)")
                                    #    print(bundle_text)
                        row1.append(final_text+"\n")
                        row1.append(action_bundle_line+"\n")
                        break
                    else:
                        final_text = "Some Other:  " + case
                        row1.append(final_text)
                        row1.append("NA")
                        break
            elif re.search(">\s{2,}((.|\n)*)alarm.*\d", data):
                row1.append("Alarm Failures")
                row1.append("NA")
            elif re.search(">\s{2,}((.|\n)*)\d", data):
                row1.append("Not a Product/testcase issue")
                row1.append("NA")
            elif re.search(">\s{2,}((.|\n)*)Error", data):
                row1.append("Error in logs")
                row1.append("NA")
            else:
                row1.append("Check logs")
                row1.append("NA")
        table.add_row(row1)

    table.title = "Date: {}\nBuild: {}\nTotal Cases: {}, Passed Cases: {}, Failed Cases: {}".format(datefrmt, build[0],
                                                                                                    str(number_test[
                                                                                                            "Total"]),
                                                                                                    str(number_test[
                                                                                                            "Pass_Case"]),
                                                                                                    str(number_test[
                                                                                                            "Fail_Case"]))

    print(table)
    tab = table.get_html_string(format=True)
    filename = suite_name + "_Bat_" + datefrmt + ".html"
    with open(filename, 'w+') as f:
        f.write(tab)

jenkins_link = "http://10.205.71.79/spark_logs/2020-06-02_14:12:36.986163"
jenkins_data = urllib.request.urlopen(jenkins_link)
json_link = "{}/{}/testrun_result.json".format(jenkins_link,re.findall("pytest-\d+", (jenkins_data.read()).decode("utf-8"))[0])
func_analysis(json_link, jenkins_link)
