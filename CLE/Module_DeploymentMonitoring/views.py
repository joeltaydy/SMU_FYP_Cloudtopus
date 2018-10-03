import json
import traceback
import requests as req
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from Module_DeploymentMonitoring.models import *
from Module_TeamManagement.models import *
from Module_DeploymentMonitoring.src import utilities,aws_util
from Module_Account.src import processLogin
from django.contrib.auth import logout

from django.http import JsonResponse
from django.template.loader import render_to_string
from Module_DeploymentMonitoring.forms import *


# Main function for setup page on faculty.
# Will retrieve work products and render to http page
#
def faculty_Setup_Base(requests,response=None):
    if response == None:
        response = {"faculty_Setup_Base" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)

    try:
        response['deployment_packages'] = {}
        response['account_number'] = ''
        response['access_key'] = ''
        response['secret_access_key'] = ''
        response['section_imageList'] = {}

        # Retrieve GitHub link from Deployment_Package
        deployment_packageObjs = Deployment_Package.objects.all()

        if len(deployment_packageObjs) > 0:
            for deployment_packageObj in deployment_packageObjs:
                response['deployment_packages'].update(
                    {
                        deployment_packageObj.deploymentid:deployment_packageObj.gitlink
                    }
                )

        # Retrieve Access_Key and Secret_Access_Key from AWS_Credentials
        aws_credentials = facultyObj.awscredential

        if aws_credentials != None:
            response['account_number']  = aws_credentials.account_number
            response['access_key'] = aws_credentials.access_key
            response['secret_access_key'] = aws_credentials.secret_access_key

            # Retrieve the team_number and account_number for each section
            course_sectionList = requests.session['courseList_updated']
            section_list = utilities.getAllTeamDetails(course_sectionList)

            if len(section_list) > 0:
                # Retreive image_id and image_name from AWS using Boto3 and compare itwith data in DB
                image_list = aws_util.getAllImages(response['account_number'],response['access_key'],response['secret_access_key'])
                for image_id,image_name in image_list.items():
                    if len(aws_credentials.imageDetails.all()) == 0:
                        image_detailsObj = utilities.addImageDetials(image_id,image_name)
                        aws_credentials.imageDetails.add(image_detailsObj)
                    else:
                        try:
                            aws_credentials.imageDetails.filter(imageId=image_id)
                        except:
                            image_detailsObj = utilities.addImageDetials(image_id,image_name)
                            aws_credentials.imageDetails.add(image_detailsObj)

                # Retrieve Shared Account Numbers from Image_Details (DB) and compared it wil data in Boto3
                images = aws_credentials.imageDetails.all()
                for image_detailObj in images:
                    id = image_detailObj.imageId
                    name = image_detailObj.imageName

                    try:
                        image_list[id] # Just to check if DB info tallies with AWS
                        for section_number,section_details in section_list.items():
                            response['section_imageList'][section_number] = {'Image_IDs':[]}
                            sharedList = []
                            nonsharedList = []

                            for team_name,account_number in section_details.items():
                                shared_account_numbers = image_detailObj.sharedAccNum
                                if shared_account_numbers == None:
                                    shared_account_numbers = []
                                else:
                                    shared_account_numbers = shared_account_numbers.split('_')

                                if account_number in shared_account_numbers:
                                    sharedList.append(
                                        {
                                            'account_number':account_number,
                                            'team_name':team_name,
                                        }
                                    )
                                else:
                                    nonsharedList.append(
                                        {
                                            'account_number':account_number,
                                            'team_name':team_name,
                                        }
                                    )

                            response['section_imageList'][section_number]['Image_IDs'].append(
                                {
                                    'image_id':id,
                                    'image_name':name,
                                    'shared_account_number':sharedList,
                                    'non_shared_account_number':nonsharedList
                                }
                            )
                    except:
                         image_detailObj.delete()

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Setup): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabSetup.html", response)

# TO-DO!!!
# Retrieval and storing of github deployment package link from instructor
# returns to faculty_Setup_Base
#
def faculty_Setup_GetGitHub(requests):
    response = {"faculty_Setup_GetGitHub" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    package_id = requests.GET.get('package_id')
    github_link = requests.GET.get('github_link')

    try:
        if package_id == None:
            raise Exception('Please input a valid package name')

        if github_link == None:
            raise Exception('Please input a valid GitHub link')

        # Save/Update GitHub link to Deployment_Package
        try:
            deployment_packageObj = Deployment_Package.objects.get(deploymentid=package_id)
            deployment_packageObj.gitlink = github_link
            deployment_packageObj.save()
        except:
            Deployment_Package.objects.create(
                deploymentid=package_id,
                gitlink=github_link,
            )
            Deployment_Package.save()

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error in Deployment Package form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


# Retrieval and storing of AWS keys from instructor
# returns to faculty_Setup_Base
#
def faculty_Setup_GetAWSKeys(requests):
    response = {"faculty_Setup_GetAWSKeys" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    account_number = requests.POST.get('account_number')
    access_key = requests.POST.get('access_key')
    secret_access_key = requests.POST.get('secret_access_key')

    try:
        if account_number == None or access_key == None or secret_access_key == None:
            raise Exception('Please input an account_number, access_key and secret_access_key')

        faculty_email = requests.user.email
        facultyObj = Faculty.objects.get(email=faculty_email)

        # Validate if account_number is a valid account_number
        valid = aws_util.validateAccountNumber(account_number,access_key,secret_access_key)
        if not valid:
            raise Exception("Invalid parameters. Please specify a valid account number.")

        # try:UPDATE, except:SAVE Account_Number, Access_Key and Secret_Access_Key to AWS_Credentials
        try:
            credentialsObj = facultyObj.awscredential
            credentialsObj.account_number = account_number
            credentialsObj.access_key = access_key
            credentialsObj.secret_access_key = secret_access_key
            credentialsObj.save()

            facultyObj.awscredential = credentialsObj
            facultyObj.save()

        except:
            credentialsObj = AWS_Credentials.objects.create(
                account_number=account_number,
                access_key=access_key,
                secret_access_key=secret_access_key,
            )
            credentialsObj.save()

            facultyObj.awscredential = credentialsObj
            facultyObj.save()

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error in AWS Information form: ' + str(e.args[0])
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


# Retrieval and storing of AMI length from instructor
# returns to faculty_Setup_Base
#
def faculty_Setup_ShareAMI(requests):
    response = {"faculty_Setup_ShareAMI" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    account_numbers = requests.GET.get('account_numbers')
    image_id = requests.GET.get('image_id')
    faculty_email = requests.user.email
    facultyObj = Faculty.objects.get(email=faculty_email)

    try:
        # Get the access_key and secret_access_key from DB
        aws_credentials = facultyObj.awscredential
        access_keys = aws_credentials.access_keys
        secret_access_keys = aws_credentials.secret_access_keys

        # Add the account number to the image permission on AWS
        client = aws_util.getClient(access_keys,secret_access_keys)
        aws_util.addUserToImage(image_id,account_numbers,client)

        for account_number in account_numbers:
            # Add the account number to DB side
            image_detailObj = aws_credentials.imageDetails.filter(imageId=image_id)[0]
            account_numbers = image_detailObj.sharedAccNum

            if account_numbers == None:
                image_detailObj.sharedAccNum = account_number
            else:
                image_detailObj.sharedAccNum = account_numbers + '_' + account_number

            image_detailObj.save()

            # Add the image to the student AWS_Credentials using their account number
            stu_credentials = AWS_Credentials.object.get(account_number=account_number)
            stu_credentials.imageDetails.add(image_detailObj)
            stu_credentials.save()

    except:
        traceback.print_exc()
        response['error_message'] = 'Error in Share AMI form: ' + e.args[0]
        return faculty_Setup_Base(requests,response)

    return faculty_Setup_Base(requests,response)


# Main function for monitor page on faculty.
#
def faculty_Monitor_Base(requests):
    response = {"faculty_Monitor_Base" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    section_num = requests.GET.get('section_number')
    response['server_status'] = {}
    response['webapp_status'] = {}

    if section_num == None:
        raise Exception('Please specify a section_number')

    try:
        # Retrieve the team_number and account_number for each section
        course_sectionList = requests.session['courseList_updated']
        section_details = utilities.getAllTeamDetails(course_sectionList)[section_num]

        for team_number,account_number in section_details.items():
            server = Server_Details.objects.filter(account_number=account_number)
            server_ip = server.IP_address
            server_state = server.state
            stu_credentials = server.account_number

            # Rule of thumb, if webapp is alive, then server will most definitely be alive
            # BUT if server is alive, there's no guarantee that webapp is alive

            # Step 1: Check if server is alive
            resource = aws_util.getResource(stu_credentials.access_key,stu_credentials.secret_access_key,service='ec2')
            instance = resource.Instance(server.instanceid)
            instance_state = instance.state

            if instance_state['code'] == 16:
                server_state = 'Live'
            elif instance_state['code'] == 0:
                server_state = 'Pending'
            elif instance_state['code'] == 32 or instance_state['code'] == 48:
                server_state = 'Killed'
            elif instance_state['code'] == 80 or instance_state['code'] == 64:
                server_state = 'Down'

            response['server_status'][team_number] = server_state

            # Step 2: Update server.state on server status
            server.state = server_state
            Server_Details.save()

            if status == 'Live':
                # Step 3: IF server 'Live', then check if webapp is 'Live'
                try:
                    webapp_url = 'http://' + server_ip + ":8000/supplementary/health_check/"
                    webapp_response = req.get(webapp_url)
                    webapp_jsonObj = json.loads(webapp_response.content.decode())

                    if webapp_jsonObj['HTTPStatusCode'] == 200:
                        response['webapp_status'][team_number] = {server_ip:'Live'}
                        
                except requests.ConnectionError:
                    response['webapp_status'][team_number] = {server_ip:'Down'}

            else:
                # Step 4: ELSE webapp is definitely 'Down'
                response['webapp_status'][team_number] = {server_ip:'Down'}

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Monitoring): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabMonitor.html", response)

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabMonitor.html", response)

# TO-DO!!!
# Main function for event configuration page on faculty.
#
def faculty_Event_Base(requests):
    response = {"faculty_Event_Base" : "active"}

    # Redirect user to login page if not authorized and student
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests, 'Module_Account/login.html', response)

    try:
        pass
    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of information (Event Configuration): ' + str(e.args[0])
        return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)

    return render(requests, "Module_TeamManagement/Instructor/ITOpsLabEvent.html", response)


# Main function for deploy page on student.
# Will check if images has been shared by faculty
#
def student_Deploy_Base(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
    except:

        logout(requests)
        return render(requests,'Module_Account/login.html',response)
    coursesec = ""
    student_email = requests.user.email
    courseList = requests.session['courseList_updated']
    for course_title, crse in courseList.items():
        if course_title == "EMS201":
            coursesec = crse['id']
    class_studentObj = Class.objects.filter(student= student_email).get(course_section=coursesec )

    awsAccountNumber =  class_studentObj.awscredential
    response['submittedAccNum'] = awsAccountNumber #Could be None or aws credentials object
    try:
        awsImage = awsAccountNumber.imageDetails #Could be None or aws image object
        response['awsImage'] = awsImage
    except:
        response['awsImage'] = None

    response["studentDeployBase"] = "active"
    print(response)
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)


# Processes Form
#
def student_Deploy_Upload(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
        if requests.method == "GET" :
            response['error_message'] = "Wrong entry to form"
            return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)
    accountNum = requests.POST.get("accountNum") #string of account number

    ipAddress = requests.POST.get("ipaddress") #string of IP address

    if accountNum is not None:
        student_Deploy_AddAccount(requests)
    elif ipAddress is not None:
        student_Deploy_AddIP(requests)

    return HttpResponse('')


# Storing of student user account number in database
#
def student_Deploy_AddAccount(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
        if requests.method == "GET" :
            response['error_message'] = "Wrong entry to form"
            return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    accountNum = requests.POST.get("accountNum") #string of account number
    print(accountNum)
    utilities.addAWSCredentials(accountNum, requests) #creates an incomplete account object


# Storing and validating of student user IP address
#
def student_Deploy_AddIP(requests):
    response = {}
    try:
        processLogin.studentVerification(requests)
        if requests.method == "GET" :
            response['error_message'] = "Wrong entry to form"
            return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    ipAddress = requests.POST.get("ipaddress") #string of IP address
    utilities.addAWSKeys(ipAddress,requests)
    utilities.addServerDetails(ipAddress,requests)


def ITOpsLabStudentDeploy(requests):
    response = {"ITOpsLabStudentDeploy" : "active"}
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentDeploy.html", response)

def ITOpsLabStudentMonitor(requests):
    response = {"ITOpsLabStudentMonitor" : "active"}
    return render(requests, "Module_TeamManagement/Student/ITOpsLabStudentMonitor.html", response)

#test forms
def server_list(request):
    servers = Server_Details.objects.all()
    return render(request, 'Module_TeamManagement/Datatables/server_list.html', {'servers': servers})


def save_server_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            servers = Server_Details.objects.all()
            data['html_server_list'] = render_to_string('Module_TeamManagement/Datatables/partial_server_list.html', {
                'servers': servers
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def server_create(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
    else:
        form = ServerForm()
    return save_server_form(request, form, 'Module_TeamManagement/Datatables/partial_server_create.html')


def server_update(request, pk):
    server = get_object_or_404(Server_Details, pk=pk)
    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
    else:
        form = ServerForm(instance=server)
    return save_server_form(request, form, 'Module_TeamManagement/Datatables/partial_server_update.html')


def server_delete(request, pk):
    server = get_object_or_404(Server_Details, pk=pk)
    data = dict()
    if request.method == 'POST':
        server.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        servers = Server_Details.objects.all()
        data['html_server_list'] = render_to_string('Module_TeamManagement/Datatables/partial_server_list.html', {
            'servers': servers
        })
    else:
        context = {'server': server}
        data['html_form'] = render_to_string('Module_TeamManagement/Datatables/partial_server_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)
#end of test forms


#deployment package forms
def deployment_package_list(request):
    dps = Deployment_Package.objects.all()
    return render(request, 'dataforms/deploymentpackage/dp_list.html', {'dps': dps})


def save_dp_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            dps = Deployment_Package.objects.all()
            data['html_dp_list'] = render_to_string('dataforms/deploymentpackage/partial_dp_list.html', {
                'dps': dps
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def dp_create(request):
    if request.method == 'POST':
        form = DeploymentForm(request.POST)
    else:
        form = DeploymentForm()
    return save_dp_form(request, form, 'dataforms/deploymentpackage/partial_dp_create.html')


def dp_update(request, pk):
    dp = get_object_or_404(Deployment_Package, pk=pk)
    if request.method == 'POST':
        form = DeploymentForm(request.POST, instance=dp)
    else:
        form = DeploymentForm(instance=dp)
    return save_dp_form(request, form, 'dataforms/deploymentpackage/partial_dp_update.html')


def dp_delete(request, pk):
    dp = get_object_or_404(Deployment_Package, pk=pk)
    data = dict()
    if request.method == 'POST':
        dp.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        dps = Deployment_Package.objects.all()
        data['html_dp_list'] = render_to_string('dataforms/deploymentpackage/partial_dp_list.html', {
            'dps': dps
        })
    else:
        context = {'dp': dp}
        data['html_form'] = render_to_string('dataforms/deploymentpackage/partial_dp_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)
#end of deployment package forms
