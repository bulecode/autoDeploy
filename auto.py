# coding=gbk

import argparse
import paramiko
import os

__author__ = "wangcan"

def main():

    """
        �����Զ����windows��ָ����maven��Ŀ���ϴ���ָ��������ָ��Ŀ¼
    :return:
    """
    args = argparse.ArgumentParser()
    args.add_argument("-s", "--src", type=str, help="src director")
    args.add_argument("-d", "--dst", type=str, help="dist director")
    args.add_argument("--host", type=str)
    args.add_argument("--user", type=str)
    args.add_argument("--password", type=str)
    args.add_argument("-b", "--build", type=bool, default=False)

    params = args.parse_args()

    if params.src is None or params.dst is None or params.host is None or params.user is None or params.password is None:
        args.print_help()
        return 0


    isBuild = params.build
    if isBuild:
        print "��Ŀ�����......"
        ret = os.popen("mvn clean package -f E:/project/edr/base/ -Dmaven.test.skip=true")
        if "BUILD FAILURE" in "".join(ret.readlines()):
            print "��Ŀ���ʧ��"
            return -1
        print "��Ŀ����ɹ�"


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "�������ӵ�Ŀ������......"
    ssh.connect(params.host, 22, params.user, params.password)
    try:
        sftp_client = ssh.open_sftp()
    except Exception,ex:
        print ("����ʧ�ܣ�%s" % ex)
    print "�Ѿ����ӵ�%s@%s" % (params.user,params.host)

    source_path = params.src
    dist_path = params.dst

    print "����ֹͣ��Ŀ"
    shutdown_file_path = dist_path.replace("webapps/ROOT","bin/shutdown.sh")
    path = "export JAVA_HOME=/opt/jdk; export PATH=$PATH:$JAVA_HOME/bin; " + shutdown_file_path
    input, output, err = ssh.exec_command(path, get_pty=True)
    shutdown_ret = output.readlines()
    print "ֹͣ��Ŀ�����"
    print "".join(shutdown_ret)

    # ɾ��Ŀ��Ŀ¼���ļ�
    if  dist_path == '/':
        print "���ܴ�����Ŀ¼"
        return -1
    input, output, err = ssh.exec_command("rm -rf %s" % dist_path, get_pty=True)
    output.readlines()

    # ���������ļ� ��ȡ�����ļ��к��ļ�·��
    files = []
    dirs  = []
    for dirName, subdirList, fileList in os.walk(source_path):
        dist_dir =  dist_path + dirName.replace(source_path, "").replace("\\", '/')
        dirs.append(dist_dir)
        for fileName in fileList:
            dist_file = dist_dir + "/" + fileName
            src_file = os.path.join(source_path, dirName, fileName)
            files.append((src_file, dist_file))

    #�����ļ���
    dirs.sort()
    input, output, err = ssh.exec_command("mkdir -p %s" % " ".join(dirs), get_pty=True)
    output.readlines()

    #�ϴ��ļ�
    for f in files:
        if not os.path.exists(f[0]):
            print "files %s not exist!!!!!" % f[0]
        # print(f[0] + "------------>" + f[1] + "   �Ѿ��ϴ�")
        sftp_client.put(f[0], f[1])
    pass
    print "��Ŀ�ļ��ϴ����"

    conf_properties_path = params.dst +  "/WEB-INF/classes/conf.properties"
    rootdir = os.path.dirname(__file__)
    sftp_client.put(rootdir + "/conf.properties" , conf_properties_path)
    print "conf�ļ��ϴ����"

    print "��Ŀ�ϴ��ɹ���"

if __name__ == '__main__':
    main()