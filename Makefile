ifeq ($(shell id -u),0)
    ROOT_CHECK :=
else
    $(error This Makefile must be run as root)
endif

start:
	./make_scripts/start_services

stop:
	./make_scripts/stop_services

enable:
	./make_scripts/enable_services

disable:
	./make_scripts/disable_services

copy:
	./make_scripts/copy_apps
	./make_scripts/copy_services

delete:
	./make_scripts/delete_apps
	./make_scripts/delete_services