#!/bin/bash

echo -e "=========================== GIT branch ====================================="
git branch -a -vv
echo
echo -e "=========================== GIT remote ====================================="
git remote -v
echo
echo -e "=========================== GIT status ====================================="
git status
echo
echo -e "=========================== GIT log 10 ====================================="
git log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit |head -10
echo
