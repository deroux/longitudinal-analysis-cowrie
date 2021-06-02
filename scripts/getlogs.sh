#!/bin/sh

# /home/cowrie/cowrie/var/log/cowrie
# honeypot a
scp -P 2112 -r root@104.248.253.81:/home/cowrie/cowrie/var/log/cowrie/*.json.* /Users/dominicrudigier/Documents/university/01\ UNI/06\ Semester/Bachelorarbeit/scripts/project/logs
scp -P 2112 -r root@104.248.253.142:/home/cowrie/cowrie/var/log/cowrie/*.json.* /Users/dominicrudigier/Documents/university/01\ UNI/06\ Semester/Bachelorarbeit/scripts/project/logs
scp -P 2112 -r root@104.248.245.133:/home/cowrie/cowrie/var/log/cowrie/*.json.* /Users/dominicrudigier/Documents/university/01\ UNI/06\ Semester/Bachelorarbeit/scripts/project/logs


