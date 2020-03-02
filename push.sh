#!/bin/bash
git add $1;
git commit -m "$2";
git remote add origin https://github.com/kalirootmalloc/attack.git;
git push -u origin master -f;
