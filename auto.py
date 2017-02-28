# coding=gbk

import argparse
import paramiko
import os

__author__ = "wangcan"

def main():

    """
        用于自动打包windows上指定的maven项目并上传到指定主机的指定目录
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
        print "项目打包中......"
        ret = os.popen("mvn clean package -f E:/project/edr/base/ -Dmaven.test.skip=true")
        if "BUILD FAILURE" in "".join(ret.readlines()):
            print "项目打包失败"
            return -1
        print "项目打包成功"


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "正在连接到目标主机......"
    ssh.connect(params.host, 22, params.user, params.password)
    try:
        sftp_client = ssh.open_sftp()
    except Exception,ex:
        print ("连接失败：%s" % ex)
    print "已经连接到%s@%s" % (params.user,params.host)

    source_path = params.src
    dist_path = params.dst

    print "正在停止项目"
    shutdown_file_path = dist_path.replace("webapps/ROOT","bin/shutdown.sh")
    path = "export JAVA_HOME=/opt/jdk; export PATH=$PATH:$JAVA_HOME/bin; " + shutdown_file_path
    input, output, err = ssh.exec_command(path, get_pty=True)
    shutdown_ret = output.readlines()
    print "停止项目结果："
    print "".join(shutdown_ret)

    # 删除目标目录的文件
    if  dist_path == '/':
        print "不能传到根目录"
        return -1
    input, output, err = ssh.exec_command("rm -rf %s" % dist_path, get_pty=True)
    output.readlines()

    # 遍历本地文件 获取所有文件夹和文件路径
    files = []
    dirs  = []
    for dirName, subdirList, fileList in os.walk(source_path):
        dist_dir =  dist_path + dirName.replace(source_path, "").replace("\\", '/')
        dirs.append(dist_dir)
        for fileName in fileList:
            dist_file = dist_dir + "/" + fileName
            src_file = os.path.join(source_path, dirName, fileName)
            files.append((src_file, dist_file))

    #创建文件夹
    dirs.sort()
    input, output, err = ssh.exec_command("mkdir -p %s" % " ".join(dirs), get_pty=True)
    output.readlines()

    #上传文件
    for f in files:
        if not os.path.exists(f[0]):
            print "files %s not exist!!!!!" % f[0]
        # print(f[0] + "------------>" + f[1] + "   已经上传")
        sftp_client.put(f[0], f[1])
    pass
    print "项目文件上传完成"

    conf_properties_path = params.dst +  "/WEB-INF/classes/conf.properties"
    rootdir = os.path.dirname(__file__)
    sftp_client.put(rootdir + "/conf.properties" , conf_properties_path)
    print "conf文件上传完成"

    print "项目上传成功！"

if __name__ == '__main__':
    main()