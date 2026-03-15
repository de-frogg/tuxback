APP=tuxback

install:
	chmod +x tuxback install.sh uninstall.sh
	./install.sh

uninstall:
	/opt/tuxback/uninstall.sh || true
	hash -r || true

run:
	python3 cli.py --help

status:
	./tuxback status

version:
	./tuxback --version

backup-test:
	./tuxback backup test_data

scheduler-run:
	./tuxback run-scheduler

docker-build:
	docker build -t $(APP) .

docker-run:
	docker run --rm $(APP)

help:
	@echo "Available commands:"
	@echo "  make install"
	@echo "  make uninstall"
	@echo "  make run"
	@echo "  make status"
	@echo "  make version"
	@echo "  make backup-test"
	@echo "  make scheduler-run"
	@echo "  make docker-build"
	@echo "  make docker-run"