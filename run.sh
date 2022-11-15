pkill -f "cluster_server.py"
rm nohup.out
nohup python3 cluster_server.py 8080 &
nohup python3 cluster_server.py 8081 &
nohup python3 cluster_server.py 8082 &