ifeq ($(shell id -u),0)
    ROOT_CHECK :=
else
    $(error This Makefile must be run as root)
endif

start:
	./make_scripts/start_services.sh

stop:
	./make_scripts/stop_services.sh

enable:
	./make_scripts/enable_services.sh

disable:
	./make_scripts/disable_services.sh

copy:
	./make_scripts/copy_apps.sh
	./make_scripts/copy_services.sh

delete:
	./make_scripts/delete_apps.sh
	./make_scripts/delete_services.sh