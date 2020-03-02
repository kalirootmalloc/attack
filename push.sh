#!/bin/bash
git add ./;
git commit -m "$1";
git remote add origin https://github.com/kalirootmalloc/attack.git;
git push -u origin master ;
