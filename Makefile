.PHONY: clean data lint format requirements sync_data_down sync_data_up

#################################################################################
# GLOBALS                                                                       #
#################################################################################
.ONESHELL:

SHELL=/bin/bash
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = on_field_gear_compliance_hackathon
PYTHON_VERSION = 3.9
PYTHON_INTERPRETER = python


#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
requirements:
ifeq ($(shell echo $$CONDA_DEFAULT_ENV),$(PROJECT_NAME))
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
else
	@echo "Make sure you activate your virtual environment"
	@echo "conda activate $(PROJECT_NAME)"
endif

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
lint:
	flake8 $(PROJECT_NAME)
	black --check --config pyproject.toml $(PROJECT_NAME)


## Format source code with black
format:
	black --config pyproject.toml $(PROJECT_NAME)


## Create the conda environment
create_env:
	@if [ -n "$(shell conda env list | grep -w $(PROJECT_NAME))" ]; then \
		echo "Conda Environment Found"; \
	else \
		echo "Creating conda environment '$(PROJECT_NAME)'."; \
		conda create --name $(PROJECT_NAME) python=$(PYTHON_VERSION) -y; \
	fi


## Initialize git project
init_git:
ifeq ('$(wildcard .git)','')
	git init
	pre-commit install
	git add requirements.txt Makefile setup.py README.md pyproject.toml .pre-commit-config.yaml
else
	@echo "Git already initialized"
endif


## Initialize dvc project
init_dvc: init_git
ifeq ('$(wildcard data.dvc)','')
	dvc init
	dvc config cache.type reflink,copy
	dvc remote add -d origin gs://fmt-ds-bucket/projects/$(PROJECT_NAME)
	dvc config core.autostage true
	dvc add data
	dvc add models
	dvc push
	git add data.dvc models.dvc .dvc/config
else
	@echo "DVC already initialized"
endif



define usage
# To activate this environment, use
#
#     $ conda activate $(PROJECT_NAME)
#
# To deactivate an active environment, use
#
#     $ conda deactivate
endef


## Initialize environment, git & dvc
update_env:
ifeq ($(shell echo $$CONDA_DEFAULT_ENV),$(PROJECT_NAME))
	@make requirements
	@make init_git
	@make init_dvc
else
	@echo "Make sure you activate your virtual environment"
	@echo "conda activate $(PROJECT_NAME)"
endif


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
