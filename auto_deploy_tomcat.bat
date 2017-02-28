@echo "manager up....."
@python e:/project/autoDeploy/auto.py -s E:/project/edr/manager/target/manager-1.0-SNAPSHOT -d /opt/edr/manager/webapps/ROOT  --host 10.11.1.191 --user root --password 123456 -b true
@echo "interface up......"
@python e:/project/autoDeploy/auto.py -s E:/project/edr/interface/target/edr-interface-1.0-SNAPSHOT -d /opt/edr/interface/webapps/ROOT  --host 10.11.1.191 --user root --password 123456

@pause
