# image_name := $(shell pwd | xargs basename)
image_name := cpp_developer

base_dir := ~/pro
distcc_port := 3632

all:
	./scripts/docker_build.sh $(image_name)
run:
	./scripts/docker_run.sh $(image_name) $(distcc_port) $(base_dir)
rund:
	./scripts/docker_run.sh $(image_name) $(distcc_port) $(base_dir) detached
attach:
	./scripts/docker_attach.sh $(image_name)
update:
	./scripts/docker_update.sh $(image_name)
clean:
	./scripts/docker_cleanup.sh