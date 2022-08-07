import os,sys,re,pymysql,time

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 使用docker目录，使用docker运行程序评分，更安全

# 本脚本用于对用户提交进行自动化评分
# 0. 切换到测试目录并解压源文件
# 1. 从数据库读取未评分行
# 2. 将上传的文件拷贝到测试目录
# 3. 在测试目录运行并将结果输出到tmp.txt
# 4. 读取txt的结果得到分数1,2
# 5. 运行脚本判断得分3，检测注释数量
# 6. 写会数据库得分，1/2/3
# 7. 删除测试目录下的数据
# 8. 给用户发邮件告知分数

def score3(f1,f2):
    try:
        fp1 = open(f1, 'r')
        fp2 = open(f2, 'r')
        if fp1 == None or fp2 == None:
            print ('文件无法打开，评分将为0！')
            return 0
        lines1 = fp1.readlines()
        cnt = 0
        for l1 in lines1:
            mt = re.search('/\*\*',l1)
            if mt:
                cnt += 1
        lines2 = fp2.readlines()
        for l2 in lines2:
            mt = re.search('/\*\*',l2)
            if mt:
                cnt += 1
        fp1.close()
        fp2.close()
        print (cnt)
        if cnt >= 120:
            return 3
        elif cnt >= 70:
            return 2
        elif cnt >= 20:
            return 1
        else:
            return 0
    except Exception as e:
        print ('error happen in score3!'+e)
        return 0;

def score1and2(curpath,f1_path,f2_path):
    # curpath = os.getcwd()
    # os.system('mkdir '+curpath+'/check/runtest/')
    # os.system ('cp '+curpath+'/check/source/AIMDB.zip '+curpath+'/check/runtest/')
    # os.system ('cp '+curpath+'/check/source/Lab3_Test1.zip '+curpath+'/check/runtest/')
    # os.system ('cp '+curpath+'/check/source/Lab3_Test2.zip '+curpath+'/check/runtest/')
    # os.chdir (curpath+'/check/runtest/')
    # os.system ('unzip AIMDB.zip')
    # os.system ('unzip Lab3_Test1.zip')
    # os.system ('unzip Lab3_Test2.zip')
    # 拷贝executor
    os.system ('cp '+f1_path+' '+curpath+'/docker/mnt/AIMDB/system/executor.h')
    os.system ('cp '+f2_path+' '+curpath+'/docker/mnt/AIMDB/system/executor.cc')
    os.chdir (curpath+'/docker/mnt/Lab3_Test1/')
    try:
        # os.system ('python runcheck.py > score.txt')
        os.system('docker run --privileged=true -v '+curpath+'/docker/mnt:/home de82cba14ad6 bash -c "python /home/Lab3_Test1/runcheck.py > /home/Lab3_Test1/score.txt"')
    except Exception as e:
        print (e)
    s1 = 0
    try:
        f1 = open (curpath+'/docker/mnt/Lab3_Test1/score.txt')
        lines = f1.readlines ()
        for line in lines:
            mt = re.search('Pass : *\d+',line)
            if mt:
                mt2 = re.search('\d+',mt.group())
                s1 = int(mt2.group())
                break
        f1.close()
    except Exception as e:
        print ('error Lab3_Test1 score!'+e)
        # return (0,0)
    os.system ('rm score.txt')   #  debug
    os.chdir (curpath+'/docker/mnt/Lab3_Test2/')
    try:
        os.system('docker run --privileged=true -v '+curpath+'/docker/mnt:/home de82cba14ad6 bash -c "python /home/Lab3_Test2/runcheck.py > /home/Lab3_Test2/score.txt"')
        # os.system ('python runcheck.py > score.txt')
    except Exception as e:
        print (e)
    s2 = 0
    try:
        f2 = open (curpath+'/docker/mnt/Lab3_Test2/score.txt')
        lines = f2.readlines ()
        for line in lines:
            mt = re.search('Pass : *\d+',line)
            if mt:
                mt2 = re.search('\d+',mt.group())
                s2 = int(mt2.group())
                break
        f2.close()
    except:
        print ('error Lab3_Test2 score!')
    os.system ('rm score.txt')  #  debug
    os.chdir (curpath+'/docker/mnt/AIMDB/')
    os.system ('make clean')
    os.system('rm '+curpath+'/docker/mnt/AIMDB/system/executor.*')
    return s1,s2

def routine(curpath):
    # curpath = os.getcwd()
    print ('routine running...')
    fpath = curpath+'/files/'
    try:
        connect = pymysql.Connect (
            host = '127.0.0.1',
            port = 3306,
            user = 'lab3appdbuser',
            passwd = 'lab3appdbpassword',
            db = 'lab3appdb',
            charset = 'utf8'
        )
        cursor = connect.cursor ()
        sql1 = 'select * from lab3app_submission where submission_revised=False order by submission_time'
        # sql1 = 'select * from lab3app_submission order by submission_time'
        cursor.execute(sql1)
        for row in cursor.fetchall():
            print (row)
            # 获取数据，运行程序，得到评分
            sc_3 = score3(fpath+row[2],fpath+row[3])
            sc_1,sc_2 = score1and2(curpath,fpath+row[2],fpath+row[3])
            # sc_1 = 8
            # sc_2 = 14
            # sc_3 = 3
            print ('score3:', sc_3)
            print ('score1and2:', sc_1,',','sc_2',sc_2)
            sql2 = "insert into lab3app_score(score_1,score_2,score_3,score_time,submission_id) values('%d','%d','%d',utc_timestamp(),'%d')" \
                    % (sc_1,sc_2,sc_3,row[0])
            try:
                cursor.execute(sql2)
                sql3 = "update lab3app_submission set submission_revised = True where id ='%d'" % row[0]
                cursor.execute(sql3)
                # connect.commit()
                sql4 = "select * from lab3app_student where id='%d' limit 1" % row[6]
                cursor.execute(sql4)
                print ('sql4...')
                for rr in cursor.fetchall():
                    sql5 = "select * from auth_user where id='%d' limit 1" % rr[-1]
                    cursor.execute(sql5)
                    print ('sql5...')
                    for rrr in cursor.fetchall():
                        try:
                            sendemail(rrr[4],(row[1],sc_1,sc_2,sc_3))
                        except Exception as e:
                            print ('send email fails...')
                connect.commit() 
            except Exception as e:
                print (e)
                connect.rollback()
        cursor.close()
        connect.close()
    except Exception as e:
        print ('routine error happens!'+e)
    pass

def sendemail(address,scores):
    # 第三方 SMTP 服务
    mail_host="smtp.163.com"  #设置服务器
    mail_user="liugang869@163.com"    #用户名
    mail_pass="lab3appuser"   #口令  163
    sender = 'liugang869@163.com'
    receivers = [address,sender]  # 接收邮件
 
    message = MIMEText("同学你好，\n\n你在Lab3系统提交的序列号为%d，评分结果如下：\n\n小测试集满分8分，得分为%d分\n大测试集满分为9分，得分为%d分\n注释部分得分为%d分\n总得分为%d分\n\nLab3系统\n\n[防止被识别为垃圾邮件]君不见黄河之水天上来，奔流到海不复回。君不见高堂明镜悲白发，朝如青丝暮成雪。"%(scores[0],scores[1],scores[2],scores[3],scores[1]+scores[2]+scores[3]), 'plain', 'utf-8')
    message['From'] =  sender #Header('Lab3系统<'+sender+'>','utf-8')
    message['To'] = address #Header('同学你好'+'<'+address+'>','utf-8')
    subject = '[Lab3系统评分结果通知]'
    message['Subject'] = subject # Header('主题：'+subject, 'utf-8') 
    status_success = False
    for ii in range(0,3): 
        if status_success == True:
            break
        try:
            smtpObj = smtplib.SMTP_SSL(mail_host,994)
            # smtpObj = smtplib.SMTP() 
            # smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
            smtpObj.login(mail_user,mail_pass)
            try:
                smtpObj.sendmail(sender, receivers, message.as_string())
                print ("邮件发送成功")
                status_success = True
                break
            except Exception as e:
                print ('错误：',e)
                # print ("邮件发送失败")
            smtpObj.quit()

        except smtplib.SMTPException as e:
            print ("Error: 无法发送邮件"+e)
    pass

def runroutine(curpath):
    while True:
        routine(curpath)
        time.sleep(10*60)
    pass

if __name__ == '__main__':
    curpath = os.path.dirname(os.path.abspath(__file__))
    runroutine(curpath)
    # sendemail('liugang@ict.ac.cn',(10,8,9,3))
    pass

