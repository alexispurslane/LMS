build: lms.cpp
	c++ -I./include -I./ -L./lib/ -I./lib/ -I./generators/ -I./objects/ -I./nouns/ -lBearLibTerminal -std=c++11 -o lms lms.cpp

run: lms.cpp
	make build
	./lms

install: lms.cpp
	make build
	cp lms /usr/local/bin/

check: lms.cpp
	scan-build -o ./tmp/ make build
