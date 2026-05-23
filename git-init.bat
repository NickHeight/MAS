@echo off
cd /d C:\Users\Nicol\MAS
git init > git-out.txt 2>&1
git add -A >> git-out.txt 2>&1
git commit -m "Initial commit - MAS folder" >> git-out.txt 2>&1
gh repo create MAS --public --source=. --remote=origin --description "MAS" >> git-out.txt 2>&1
git push -u origin master >> git-out.txt 2>&1
git push -u origin main >> git-out.txt 2>&1
git remote -v >> git-out.txt 2>&1
echo DONE >> git-out.txt
