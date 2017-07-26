from pprint import pprint
import requests
import json
import urllib
import re
import getpass

print "Username: "
username = raw_input()
password = getpass.getpass()

"""Get jobs that are running on the Jenkins instance"""
def get_all_jobs():
    # connect to the server
    server = 'https://cdes-ci.usd.lab.emc.com/jenkins/api/json?pretty=true'

    server_response = requests.get(server, auth=(username, password))

    # initialize jobs array
    jobs = []

    # get all jobs from the jenkins server via JSON response
    data = server_response.json()
    for job in data['jobs']:
        # only search for cdes2 jobs
        if "cdes2-qual-" in job['name']:
            jobs.append(job['name'])

    # return all jobs from the jenkins server
    return jobs

"""Get builds for each job that is running on the Jenkins instance"""
def get_job_builds(job):
    print 'JOB: ' + job
    # connect to the server
    server = 'https://cdes-ci.usd.lab.emc.com/jenkins/job/' + job + '/api/json?pretty=true'

    server_response = requests.get(server, auth=(username, password))

    # initialize builds array
    builds = []

    # get all builds for current job via JSON response
    data = server_response.json()
    for build in data['builds']:
        builds.append(build['number'])

    # return all builds for current job
    return builds

"""Get tests for each build that is running on the Jenkins instance"""
def get_build_tests(job, build):
    print '-----BUILD-----: ' + build
    # connect to the server
    server = 'https://cdes-ci.usd.lab.emc.com/jenkins/job/' + job + '/' + build + '/artifact/tests/test_result.html'

    server_response = requests.get(server, auth=(username, password))

    if server_response.status_code != 200:
        server = 'https://cdes-ci.usd.lab.emc.com/jenkins/job/' + job + '/' + build + '/artifact/expander/tests/test_result.html'
        server_response = requests.get(server, auth=(username, password))

    data = server_response.text

    # initialize tests array
    tests = []

    # find the name of the test
    regex = "<a onClick=\"ExpandDetail\(\)\" href=\"#(.*)\""
    test_names = re.findall(regex, data)

    # find the status of the test
    regex = "<a onClick=\"ExpandDetail\(\)\" href=\".*\".*\n\s*<td class=\"(.*)\""
    test_status = re.findall(regex, data)

    # create an array of [name, status] pairs
    for i in range(0, len(test_names)):
        tests.append([test_names[i], test_status[i]])

    test_status_count(test_status)

    # return all tests for the current build
    return tests

def test_status_count(test_status):
    print "Total Tests: " + str(len(test_status))

    # initialize all status counts
    pass_count = 0
    fail_count = 0
    skip_count = 0
    expected_count = 0
    other_count = 0

    # increment the count for each test
    for i in range(0, len(test_status)):
        if test_status[i] == "pass":
            pass_count += 1
        elif test_status[i] == "fail":
            fail_count += 1
        elif test_status[i] == "skip":
            skip_count += 1
        elif test_status[i] == "expected":
            expected_count += 1
        else:
            other_count += 1

    print "Pass: " + str(pass_count) + " Fail: " + str(fail_count) + " Skip: " + str(skip_count) + " Expected: " + str(expected_count) + " Other: " + str(other_count)
    # return a list of statuses
    return [pass_count, fail_count, skip_count, expected_count, other_count]

if __name__ == '__main__':
    # get all jobs from our jenkins server
    jobs = get_all_jobs()
    builds = []
    tests = []

    # get all builds for each job
    for job in jobs:
        builds = get_job_builds(job)
        # get all tests for each build
        for build in builds:
            tests = get_build_tests(str(job), str(build))

# TODO: check a failed test across all platforms to see if it is specific to that platform
# TODO: check a failed test against the last build to see if it is a regression
# TODO: check a failed test against past 20 tests to see if it is expected
