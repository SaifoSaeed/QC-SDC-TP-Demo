SHELL :=  cmd.exe
.PHONY: clean run_real run_sim ani all svdeps chdeps deps

all: deps chdeps svdeps clean run_real ani

svdeps:
	uv pip freeze > requirements.txt

chdeps:
	uv pip check

deps:
	uv pip install -r requirements.txt

run_sim:
	python main.py -p sdc
	python main.py -p tp
	python ani.py

run_real:
	python main.py -p sdc -r
	python main.py -p tp -r
	python ani.py

clean:
	-rmdir /s /q json_files output_files
	mkdir json_files output_files\tp output_files\sdc