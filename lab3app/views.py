from django.shortcuts import render
import time,sys,os
from django.contrib.auth.models import User
from lab3app.models import Student,SerailNo,Group,StudentGroup,Message,Suggestion,Submission,Score
from django.contrib import auth
from django import forms

# Create your views here.

def signin(request):
    context = {}
    return render(request,'lab3app/signin.html',context)

def signinform(request):
    try:
        if request.method=='POST':
            username=request.POST.get('inputEmail')
            password=request.POST.get('inputPassword')
            user= auth.authenticate(username=username,password=password)
            if user and user.is_active:
                auth.login(request, user)
                student = Student.objects.filter(student_user_id=user.id)
                return render(request,'lab3app/welcome.html',{'user_name':student[0].student_name})
            else:
                return render(request,'lab3app/signin.html',{'status_signin':'用户未注册或密码错误！'+username})
    except Exception as e:
        return render(request,'lab3app/signin.html',{'status_signin':'登录异常！'+str(e)})
    return render(request,'lab3app/signin.html',{'status_signin':'登录异常！'})

def register(request):
    return render(request,'lab3app/register.html',{})

def registerform(request):
    curtime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
    if request.user.is_authenticated:
        return render(request,'lab3app/register.html',{'status_register':'当前用户已登录！'})
    try:
        if request.method=='POST':

            username = request.POST.get('inputEmail')
            password1 = request.POST.get('inputPassword')
            studentid = request.POST.get('inputStudentId')
            studentname = request.POST.get('inputStudentName')

            filterResult=User.objects.filter(username=username)
            if len(filterResult)>0:
                return render(request,'lab3app/register.html',{'status_register':'当前用户已存在！'})
            
            user=User()
            user.username=username
            user.set_password(password1)
            user.save()
            #用户扩展信息 profile
            # profile=UserProfile()#e*************************
            # profile.user_id=user.id
            # profile.phone=phone
            # profile.save()
            student = Student()
            student.student_user_id = user.id
            student.student_id = studentid
            student.student_name = studentname
            student.student_regiter_time = curtime
            student.student_is_leader = False
            student.save()
            return render(request,'lab3app/register.html',{'status_register':'注册成功，请登录！'})

    except Exception as e:
        print (str(e))
        return render(request,'lab3app/register.html',{'status_register':'注册表单提交异常！'+str(e)})
    return render(request,'lab3app/register.html',{'status_register':'注册表单提交异常！'+'FinalError!'})

def index(request):
    context = {}
    return render(request,'lab3app/index.html',context)
def base(request):
    context = {}
    return render(request,'lab3app/base.html',context)

def welcome(request):
    if request.user.is_authenticated:
        user = request.user
        student = Student.objects.filter(student_user_id=user.id)
        return render(request,'lab3app/welcome.html',{'user_name':student[0].student_name})
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def personal(request):
    if request.user.is_authenticated:
        user = request.user
        # student info
        students = Student.objects.filter(student_user_id=user.id)
        student = {}
        student['student_name'] = students[0].student_name
        student['student_id'] = students[0].student_id
        student['student_email'] = user.username
        student['student_register_time'] = students[0].student_regiter_time
        context = {}
        context['student'] = student
        # group info
        studentgroups = StudentGroup.objects.filter(student=students[0])
        if len(studentgroups) == 1:
            group = studentgroups[0].group
            group_info = {}
            group_info['group_name'] = group.group_name
            group_info['group_leader'] = group.group_leader.student_name

            studentgroups2 = StudentGroup.objects.filter(group=group)
            group_member = []
            for sg in studentgroups2:
                group_member.append(sg.student.student_name)

            group_info['group_members'] = ','.join(group_member)
            group_info['group_serial'] = group.group_serial
            group_info['group_register_time'] = group.group_register_time
            context['group'] = group_info
        # submission info
        submissions = Submission.objects.filter(submission_student=students[0])
        if len(submissions) == 0:
            # context['status_personal'] = "该用户暂无提交记录！"
            return render(request,'lab3app/personal.html',context)
        mysubmission = []
        for ss in submissions:
            ssi = {}
            ssi['submission_serial'] = ss.submission_serial
            ssi['submission_time'] = ss.submission_time
            ssi['submission_revised'] = ss.submission_revised
            if ss.submission_revised == True:
                scores = Score.objects.filter(submission=ss)
                if len(scores) == 1:
                    ssi['score_time'] = scores[0].score_time
                    ssi['score_total'] = scores[0].score_1+scores[0].score_2+scores[0].score_3
            mysubmission.append(ssi)
        context['submissions'] = mysubmission
        # context['status_personal'] = str(len(mysubmission))
        return render(request,'lab3app/personal.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

    # student = {'student_name':'刘刚','student_id':'201618013229015', 'student_email':'liugang@ict.ac.cn','student_register_time':'2018-11-23 15:20:35' }
    # item = {'submission_serial':'1','submission_time':'2018-11-23 16:20:36','submission_revised':'True','score_time':'2018-11-24 00:00:01', 'score_total': 20}
    # submissions = [item]
    # context = {'student':student,'submissions':submissions}
    # return render(request,'lab3app/personal.html',context)

def score(request):
    if request.user.is_authenticated:
        context = {}
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        studentgroups = StudentGroup.objects.filter(student=students[0])
        if len(studentgroups) == 0:
            return render(request,'lab3app/score.html',context)
        studentgroups2 = StudentGroup.objects.filter(group=studentgroups[0].group)
        group_submission = None
        for sg2 in studentgroups2:
            submissions = Submission.objects.filter(submission_student=sg2.student)
            for s in submissions:
                if s.submission_revised == True:
                    if group_submission == None:
                        group_submission = s
                    else:
                        if s.submission_time > group_submission.submission_time:
                            group_submission = s
        if group_submission != None:
            scores = Score.objects.filter(submission=group_submission)
            student = {'student_id':students[0].student_id,'student_name':students[0].student_name}
            score = {}
            score['score_1'] = scores[0].score_1
            score['score_2'] = scores[0].score_2
            score['score_3'] = scores[0].score_3
            score['score_total'] = scores[0].score_1+scores[0].score_2+scores[0].score_3
            context['student'] = student
            context['score'] = score
        return render(request,'lab3app/score.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def showgroupmessage(user):
    students = Student.objects.filter(student_user_id=user.id)
    messages = Message.objects.filter(message_to=students[0])
    ret_m = []
    for message in messages:
        mm = {}
        mm['message_from'] = message.message_from.student_name
        mm['message_to'] = message.message_to.student_name
        mm['message_request_or_answer'] = message.message_request_or_answer
        mm['message_join_or_quit'] = message.message_join_or_quit
        mm['message_time'] = message.message_time
        mm['message_revised'] = message.message_revised
        mm['message_id'] = message.id
        ret_m.append(mm)
    return ret_m

def creategroup(request):
    if request.user.is_authenticated:
        context = {}
        groupmessage = showgroupmessage(request.user)
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        context['student_name'] = students[0].student_name
        context['messages'] = showgroupmessage(user)
        context['student_is_leader'] = students[0].student_is_leader
        return render(request,'lab3app/creategroup.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def creategroupform(request):
    if request.user.is_authenticated:
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        # 检测创建分组者不在任何一个分组
        studentgroups = StudentGroup.objects.filter(student=students[0])
        context = {}
        context['student_is_leader'] = students[0].student_is_leader
        context['messages'] = showgroupmessage(user)
        context['student_name'] = students[0].student_name,
        if len(studentgroups)>0:
            context['status_creategroup'] = '创建分组不成功，当前用户已分组！如需创建，请先退出当前分组'
            return render(request,'lab3app/creategroup.html',context)
        # 检测序列号存在
        serialnos = SerailNo.objects.filter()
        if len(serialnos) != 1:
            context['status_creategroup'] = '分组序列号有误！'
            return render(request,'lab3app/creategroup.html',context)
        group_serial = serialnos[0].serial_group
        group_name = request.POST.get('group_name')
        # 检测组名冲突
        groups = Group.objects.filter(group_name=group_name)
        if len(groups)>0:
            context['status_creategroup'] = '创建分组不成功，组名冲突！请重新选择组名！'
            return render(request,'lab3app/creategroup.html',context)
        # 创建分组
        group_leader = students[0]
        group = Group()
        group.group_serial = group_serial
        group.group_name = group_name
        group.group_leader = group_leader
        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
        group.group_register_time = curtime
        group.save()
        # 创建分组者自动加入分组
        studentgroup = StudentGroup()
        studentgroup.student = students[0]
        studentgroup.group = group
        studentgroup.join_time =curtime
        studentgroup.save()
        # 序列号自增
        serialnos[0].serial_group += 1
        serialnos[0].save()
        # 组长标记
        Student.objects.filter(student_user_id=user.id).update(student_is_leader=True)
        context['status_creategroup'] = '成功创建分组！你的分组全局可见，请让组员申请加入你的分组！'
        return render(request,'lab3app/creategroup.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def joingroup(request):
    if request.user.is_authenticated:
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        studentgroups = StudentGroup.objects.filter(student=students[0])
        # 分组信息
        context = {'status_creategroup':None,'groups':[]}
        if len(studentgroups)>0:
            context['status_creategroup'] = "当前用户已分组！如需加入其他分组请先退出当前分组！"
        messages = Message.objects.filter(message_from=students[0],message_revised=False)
        if len(messages)>0:
            context['status_creategroup'] = "当前用户正在请求加入分组，请联系组长进行操作！"
        groups = Group.objects.filter()
        for group in groups:
            group_info = {}
            group_info['group_name'] = group.group_name
            group_info['group_leader'] = group.group_leader.student_name
            studentgroups2 = StudentGroup.objects.filter(group=group)
            group_member = []
            for sg in studentgroups2:
                group_member.append(sg.student.student_name)
            group_info['group_members'] = ','.join(group_member)
            group_info['group_serial'] = group.group_serial
            group_info['group_register_time'] = group.group_register_time
            context['groups'].append(group_info)
        context['student_is_leader'] = students[0].student_is_leader
        context['messages'] = showgroupmessage(user)
 
        return render(request,'lab3app/joingroup.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def joingroupform(request,group_serial):
    if request.user.is_authenticated:
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        studentgroups = StudentGroup.objects.filter(student=students[0])
        messages = Message.objects.filter(message_from=students[0],message_revised=False)
        # 分组信息
        context = {'status_joingroup':None,'groups':[]}
        group_serial_int = int(group_serial)
        groups2 = Group.objects.filter(group_serial=group_serial_int)
        studentgroups2 = StudentGroup.objects.filter(group=groups2[0])
        if len(studentgroups)>0 or len(messages)>0 or len(studentgroups2)>3:
            context['status_joingroup'] = "当前用户已分组或正在分组或当前分组已满3人！"
            groups = Group.objects.filter()
            for group in groups:
                group_info = {}
                group_info['group_name'] = group.group_name
                group_info['group_leader'] = group.group_leader.student_name
                studentgroups2 = StudentGroup.objects.filter(group=group)
                group_member = []
                for sg in studentgroups2:
                    group_member.append(sg.student.student_name)
                group_info['group_members'] = ','.join(group_member)
                group_info['group_serial'] = group.group_serial
                group_info['group_register_time'] = group.group_register_time
                context['groups'].append(group_info)
            context['student_is_leader'] = students[0].student_is_leader
            context['messages'] = showgroupmessage(user)
            return render(request,'lab3app/joingroup.html',context)
        message = Message()
        message.message_from = students[0]
        message.message_to = groups2[0].group_leader
        message.message_request_or_answer = True
        message.message_join_or_quit = True
        message.message_revised = False
        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
        message.message_time = curtime
        message.save()
        context['status_joingroup'] = "请求分组消息已发送，请联系组长同意请求！"
        groups = Group.objects.filter()
        for group in groups:
            group_info = {}
            group_info['group_name'] = group.group_name
            group_info['group_leader'] = group.group_leader.student_name
            studentgroups2 = StudentGroup.objects.filter(group=group)
            group_member = []
            for sg in studentgroups2:
                group_member.append(sg.student.student_name)
            group_info['group_members'] = ','.join(group_member)
            group_info['group_serial'] = group.group_serial
            group_info['group_register_time'] = group.group_register_time
            context['groups'].append(group_info)
        context['messages'] = showgroupmessage(user)
        context['student_is_leader'] = students[0].student_is_leader
        return render(request,'lab3app/joingroup.html',context)
     
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def quitgroup(request):
    if request.user.is_authenticated:
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        studentgroups = StudentGroup.objects.filter(student=students[0])
        # 分组信息
        context = {}
        if len(studentgroups)>0:
            group = studentgroups[0].group
            group_info = {}
            group_info['group_name'] = group.group_name
            group_info['group_leader'] = group.group_leader.student_name
            studentgroups2 = StudentGroup.objects.filter(group=group)
            group_member = []
            for sg in studentgroups2:
                group_member.append(sg.student.student_name)
            group_info['group_members'] = ','.join(group_member)
            group_info['group_serial'] = group.group_serial
            group_info['group_register_time'] = group.group_register_time
            context['groups'] = [group_info]
        context['messages'] = showgroupmessage(user)
        context['student_is_leader'] = students[0].student_is_leader
 
        return render(request,'lab3app/quitgroup.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def quitgroupform(request,group_serial):
    if request.user.is_authenticated:
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        context = {'groups':[]}
        context['student_is_leader'] = students[0].student_is_leader
        messages = Message.objects.filter(message_from=students[0],message_revised=False)
        if len(messages)>0:

            studentgroups2 = StudentGroup.objects.filter(student=students[0])
            groups = [studentgroups2[0].group]
            for group in groups:
                group_info = {}
                group_info['group_name'] = group.group_name
                group_info['group_leader'] = group.group_leader.student_name
                studentgroups2 = StudentGroup.objects.filter(group=group)
                group_member = []
                for sg in studentgroups2:
                    group_member.append(sg.student.student_name)
                group_info['group_members'] = ','.join(group_member)
                group_info['group_serial'] = group.group_serial
                group_info['group_register_time'] = group.group_register_time
                context['groups'].append(group_info)
 
            context['messages'] = showgroupmessage(user)
            context['status_quitgroup'] = "退出分组消息已发送，请不要多次请求！"
            return render(request,'lab3app/quitgroup.html',context)
        # 加入时保证有严格的请求
        group_serial_int = int(group_serial)
        groups2 = Group.objects.filter(group_serial=group_serial_int)
        message = Message()
        message.message_from = students[0]
        message.message_to = groups2[0].group_leader
        message.message_request_or_answer = True
        message.message_join_or_quit = False
        message.message_revised = False
        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
        message.message_time = curtime
        message.save()
        context['status_quitgroup'] = "退出分组消息已发送，请联系组长同意退出！"
        groups = Group.objects.filter()
        for group in groups:
            group_info = {}
            group_info['group_name'] = group.group_name
            group_info['group_leader'] = group.group_leader.student_name
            studentgroups2 = StudentGroup.objects.filter(group=group)
            group_member = []
            for sg in studentgroups2:
                group_member.append(sg.student.student_name)
            group_info['group_members'] = ','.join(group_member)
            group_info['group_serial'] = group.group_serial
            group_info['group_register_time'] = group.group_register_time
            context['groups'].append(group_info)
        context['messages'] = showgroupmessage(user)
        return render(request,'lab3app/quitgroup.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def dismissgroup(request):
    if request.user.is_authenticated:
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        studentgroups = StudentGroup.objects.filter(student=students[0])
        # 分组信息
        context = {}
        if len(studentgroups)>0:
            group = studentgroups[0].group
            group_info = {}
            group_info['group_name'] = group.group_name
            group_info['group_leader'] = group.group_leader.student_name
            studentgroups2 = StudentGroup.objects.filter(group=group)
            group_member = []
            for sg in studentgroups2:
                group_member.append(sg.student.student_name)
            group_info['group_members'] = ','.join(group_member)
            group_info['group_serial'] = group.group_serial
            group_info['group_register_time'] = group.group_register_time
            context['groups'] = [group_info]
        context['messages'] = showgroupmessage(user)
        context['student_is_leader'] = students[0].student_is_leader
 
        return render(request,'lab3app/dismissgroup.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def dismissgroupform(request,group_serial):
    if request.user.is_authenticated:
        # return render(request,'lab3app/dismissgroup.html',{'status_dismissgroup':group_serial})
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        # 判断是否有未处理的消息
        messages = Message.objects.filter(message_to=students[0],message_revised=False)
        # 判断是否为组长
        if students[0].student_is_leader == False or len(messages)>0:
            # 分组信息
            studentgroups = StudentGroup.objects.filter(student=students[0])
            group = studentgroups[0].group
            group_info = {}
            group_info['group_name'] = group.group_name
            group_info['group_leader'] = group.group_leader.student_name
            studentgroups2 = StudentGroup.objects.filter(group=group)
            group_member = []
            for sg in studentgroups2:
                group_member.append(sg.student.student_name)
            group_info['group_members'] = ','.join(group_member)
            group_info['group_serial'] = group.group_serial
            group_info['group_register_time'] = group.group_register_time
            context = {}
            context['groups'] = [group_info]
            context['status_dismissgroup'] = "操作不成功，操作者不是组长或还有消息未处理！如果你是组长，请先处理分组消息！"
            context['student_is_leader'] = students[0].student_is_leader
            context['messages'] = showgroupmessage(user)
            # redirect('lab3app/dismissgroup/')
            return render(request,'lab3app/dismissgroup.html',context)
        # 设置该用户为非组长
        Student.objects.filter(student_user_id=user.id).update(student_is_leader=False)
        # 给成员发分组解散的消息并删除成员
        # group_serial = request.GET.get('group_serial')
        group_serial_int = int(group_serial)
        groups = Group.objects.filter(group_serial=group_serial_int)
        studentgroups = StudentGroup.objects.filter(group=groups[0])
        for studentgroup in studentgroups:
            message = Message()
            message.message_from = students[0]
            message.message_to = studentgroup.student
            message.message_request_or_answer = False
            message.message_join_or_quit = False
            message.message_revised = True
            curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
            message.message_time = curtime
            message.save()
            studentgroup.delete()
        # 删除组队
        groups[0].delete()
        context = {}
        context['student_is_leader'] = False
        context['messages'] = showgroupmessage(user)
        return render(request,'lab3app/dismissgroup.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 
 
def submit(request):
    if request.user.is_authenticated:
        return render(request,'lab3app/submit.html',{})
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 

def submitform(request):
    if request.user.is_authenticated:
        context = {}
        students = Student.objects.filter(student_user_id=request.user.id)
        studentgroups = StudentGroup.objects.filter(student=students[0])
        if len(studentgroups) == 0:
            context['status_submit'] = '操作不成功，当前用户不在任何分组，请先建立分组或加入分组！'
            return render(request,'lab3app/submit.html',context)
        if request.method == 'POST':
            serialnos = SerailNo.objects.filter()
            if len(serialnos) != 1:
                context['status_submit'] = '内部错误，SerialNo不存在！'
                return render(request,'lab3app/submit.html',context)
            # 如果存在未评分的提交，则不可再次提交
            schecks = Submission.objects.filter(submission_student=students[0],submission_revised=False)
            if len(schecks) > 0:
                context['status_submit'] = '操作不成功，当前用户有未评分的提交，请耐心等待评分后再提交，预期等待不超过20分钟！'
                return render(request,'lab3app/submit.html',context)
            submission = Submission()
            submission.submission_serial = serialnos[0].serial_submission
            students = Student.objects.filter(student_user_id=request.user.id)
            submission.submission_student = students[0]
            curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
            submission.submission_time = curtime
            submission.submission_revised = False
            submission.submission_file_h = request.FILES.get('executor_h',None)
            submission.submission_file_cc = request.FILES.get('executor_cc',None)
            if submission.submission_file_h == None or submission.submission_file_cc == None:
                context['status_submit'] = '操作不成功，上传文件不能为空！'
                return render(request,'lab3app/submit.html',context)
            if submission.submission_file_h.size > 1024*1024*10 or submission.submission_file_cc.size > 10*1024*1024:
                context['status_submit'] = '操作不成功，上传文件超过10MB，这不科学！'
                return render(request,'lab3app/submit.html',context)
            submission.save()
            serialnos[0].serial_submission += 1
            serialnos[0].save()
            context['status_submit'] = '文件已上传，提交成功，请耐心等待评分结果，评分结果将邮件通知！'
        else:
            context['status_submit'] = '内部错误，提交方法不是POST！'
        return render(request,'lab3app/submit.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 
    pass

def suggestion(request):
    if request.user.is_authenticated:
        return render(request,'lab3app/suggestion.html',{})
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 
 
def suggestionform(request):
    if request.user.is_authenticated:
        students = Student.objects.filter(student_user_id=request.user.id)
        suggestion = Suggestion() 
        suggestion.student = students[0]
        suggestion.suggestion_subject = request.POST.get('suggestion_subject')
        suggestion.suggestion_content = request.POST.get('suggestion_content')
        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
        suggestion.suggestion_time = curtime
        suggestion.save()
        context = {}
        context['status_suggestion'] = "你的建议已经提交成功！"
        return render(request,'lab3app/suggestion.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 
 
def signout(request):
    auth.logout(request)
    return render(request,'lab3app/signin.html',{'status_signin':'你已经退出登录！'})

#####################################
def agreemessage(request, messageid):
    if request.user.is_authenticated:
        messages = Message.objects.filter(id=messageid)
        context = {}
        if len(messages) == 0:
            context['status_groupmessage'] = '发生内部错误，消息不存在！'
            return render(request,'lab3app/groupmessage.html',context)
        # 判断是否为leader
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        context['student_is_leader'] = students[0].student_is_leader
        if students[0].student_is_leader == False:
            context['status_groupmessage'] = '发生内部错误，消息接受者不是组长！'
            return render(request,'lab3app/groupmessage.html',context)
        # 人数未满则可插入
        if messages[0].message_join_or_quit == True:
            student_r = messages[0].message_from
            student_l = messages[0].message_to
            groups = Group.objects.filter(group_leader=student_l)
            studentgroups = StudentGroup.objects.filter(group=groups[0])
            if len(studentgroups)>3:
                context['status_groupmessage'] = '操作失败，消息接受者不是组长！'
                context['messages'] = showgroupmessage(request.user)
                return render(request,'lab3app/groupmessage.html',context)
            studentgroup =StudentGroup()
            studentgroup.student = student_r
            studentgroup.group = groups[0]
            curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
            studentgroup.join_time = curtime
            studentgroup.save()
        else:
            student_r = messages[0].message_from
            StudentGroup.objects.filter(student=student_r).delete()
        # 回复消息
        message = Message()
        message.message_from = messages[0].message_to
        message.message_to = messages[0].message_from
        message.message_request_or_answer = False
        message.message_join_or_quit = True
        message.message_revised = True
        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
        message.message_time = curtime
        message.save()
        messages = Message.objects.filter(id=messageid).update(message_revised=True)
        context['status_groupmessage'] = '操作成功，你已同意请求！'
        context['messages'] = showgroupmessage(request.user)
        # 判断是否为leader
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        context['student_is_leader'] = students[0].student_is_leader
        return render(request,'lab3app/groupmessage.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 
 
def refusemessage(request, messageid):
    if request.user.is_authenticated:
        messages = Message.objects.filter(id=messageid)
        context = {}
        if len(messages) == 0:
            context['status_groupmessage'] = '发生内部错误，消息不存在！'
            return render(request,'lab3app/groupmessage.html',context)
        # 回复消息
        message = Message()
        message.message_from = messages[0].message_to
        message.message_to = messages[0].message_from
        message.message_request_or_answer = False
        message.message_join_or_quit = False
        message.message_revised = True
        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime());
        message.message_time = curtime
        message.save()
        messages = Message.objects.filter(id=messageid).update(message_revised=True)
        context['status_groupmessage'] = '操作成功，你已拒绝请求！'
        context['messages'] = showgroupmessage(request.user)
        # 判断是否为leader
        user = request.user
        students = Student.objects.filter(student_user_id=user.id)
        context['student_is_leader'] = students[0].student_is_leader
        return render(request,'lab3app/groupmessage.html',context)
    else:
        return render(request,'lab3app/signin.html',{'status_signin':'当前用户未登录！'}) 
 
