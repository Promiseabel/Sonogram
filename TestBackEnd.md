#!/bin/bash

curl -i -H "Content-Type: application/json" -X POST -d '{"username": "promise","password": "prom", "email_address": "promise", "bio":"promise"}' http://localhost:8080/signup

curl -i -H "Content-Type: application/json" -X POST -d '{"username": "promise", "password": "prom"}' -c cookie-jar -k http://localhost:8080/signin

curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://localhost:8080/signin

curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar -k http://localhost:8080/signout

curl -i -H "Content-Type: application/json" -X PUT -d '{"username": "promise","password": "prom", "email_address": "promise", "bio":"promise", "profile_picture" : "path/to/file" }' -b cookie-jar -k http://localhost:8080/users/1

curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k http://localhost:8080/users/1

curl -i -H "Content-Type: application/json" -X POST -d '{"title": "test-curl", "audio_file": "/some/random path", "parent_audio_id":5, "like_count":0}' -b cookie-jar -k http://localhost:8080/users/1

curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar -k http://localhost:8080/users/1/audios/1

curl -i -H "Content-Type: application/json" -X PUT -d '{"title": "new title", "audio_file": "/new/path"}' -b cookie-jar -k http://localhost:8080/users/1/audios/5

curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k http://localhost:8080/audios

curl -i -H "Content-Type: application/json" -X PUT -d '{"increment": true}' -b cookie-jar -k http://localhost:8080/audios/7

curl -i -H "Content-Type: application/json" -X GET http://localhost:8080/audios/1