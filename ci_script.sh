# this is for debug convenience 
# refs: https://registry.hub.docker.com/_/python/
# 1. edit dockfile
# 2. test dockerfile
#   docker build -t my-python-app .
#   sudo docker run -it --rm --name my2 -v "$(pwd)":/var/cache/drone -w /var/cache/drone my-python-app  bash wowhua_api/drone_script.sh
# 3. put the script under wowhua_api/.drone.xml

rm -r /usr/src/app
echo '====================env==================='
env
echo '====================env==================='
source /testenv/bin/activate
make config
echo '====================pip==================='
pip freeze
echo '====================pip==================='
make test
