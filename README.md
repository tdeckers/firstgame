# Overview

Inspired by: https://www.youtube.com/watch?v=r428O_CMcpI

## Initial project setup

git init
python -m venv venv
# Activate venv
.\venv\Scripts\Activate.ps1

## Update / reset project

pip install -r .\requirements.txt

## Reference

Collision detection: http://jeffreythompson.org/collision-detection/line-point.php

## TODO

Consider using pymunk physics engine for motion. Example:
https://github.com/slembcke/Chipmunk2D/blob/master/demo/Tank.c
Right now, only using pymunk for vector calc.