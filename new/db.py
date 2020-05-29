class Database():

    def insert_db(results,build,log_link):
        import subprocess
        import sys
        import datetime
        import pymysql

        pymysql.install_as_MySQLdb()
        import MySQLdb as my

        # Read the Test Parameter from the file


        product = "NSX-Transformer"

        # mysql_server = report_data_dict.get("dbIP").strip()
        # mysql_username = report_data_dict.get("dbUsername").strip()
        # mysql_username = report_data_dict.get("dbPassword").strip()
        # mysql_db = report_data_dict.get("dbName").strip()


        date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
        suiteid = "L2vpn_VLAN"
        #suite_url = resultURL + nfsReportPath + '/SuiteReport.html'

        passed_count,failed_count,pending_count = 0,0,0
        print (type(results))
        for test in results:
            if results[test] == "PASS":
                passed_count = passed_count+1
            if results[test] == "FAIL":
                failed_count = failed_count+1
            if results[test] != "PASS" and results[test] != "FAIL":
                pending_count = pending_count+1

        if failed_count > 0:
            status = "FAILED"
            executed_count = passed_count + failed_count
        else:
            status = "PASSED"
            executed_count = passed_count+failed_count


        

        total_test_cases = passed_count + failed_count + pending_count

        core = "N-A"
        suitereport = log_link
        suite_execution_time = "N-A"
        race_track = "N-A"
        
        build_cols = "nsxbuild,nsxbranch"
        build_values = str(build)

        Jnekinurl = log_link
        


        suites_col_name = "(suiteid, date, product, feature, " + build_cols + ",status, totalcases, executed, passed, failed, pending, core, suitereport, jenkinslog, duration, racetrack)"

        suites_col_values = "('" + suiteid + "', '" + date + "', '" + product + "', '" + "L2vpn_Vlan" + "', " +"'"+ build_values+"', "+"'" + "nsx-firestar" + "', " + "'" + status + "', " + str(
            total_test_cases) + ", " + str(executed_count) + ", " + str(passed_count) + ", " + str(failed_count) + ", " + str(
            pending_count) + ", '" + core + "', '" + suitereport + "', '" + Jnekinurl + "', '" + suite_execution_time + "', '" + race_track + "')"

        # Connect to MySQL DB
        # pip install pymysql
        db = my.connect(host="10.173.190.3", user="vkharge", passwd="vkharge", db="nsxt_jenkins")
        cursor = db.cursor()
        print("Connected to DB")

        # Insert Suite Record in MySQL DB
        sql = "INSERT INTO suites " + suites_col_name + " VALUES " + suites_col_values
        print("Suite Record To Insert : " + sql)
        number_of_rows = cursor.execute(sql)
        db.commit()

        for key in results:
            print (key)
            sql = "INSERT INTO testcases (suiteid, testno, testcasename, status, core, time, failedworkload, testcasepath) VALUES ('%s', %d, '%s', '%s', '%s', '%s', '%s', '%s')" % (
                                  suiteid, int(1), key, results[key], "NA",
                                  "NA", "NA", "NA")
            print("Test Case Record To Insert : " + sql)
            number_of_rows = cursor.execute(sql)
            db.commit()

        db.close()
