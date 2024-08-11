USERNAME = root
SERVER = 45.134.226.157
DEST_DIR = /root/UtrpeniChess
CODE_FILEs = ./*.py ./.venv

.PHONY: code_to_server

code_to_server: FORCE
	rsync -avzr  --delete ./ $(USERNAME)@$(SERVER):$(DEST_DIR)

venv_init:
	python3 -m venv .venv

req_save:
	pip3 freeze > requirements.txt

install: FORCE
	pip3 install -r requirements.txt

FORCE: