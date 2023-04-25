
.PHONY: all
all: test

test: test.o
	$(./compiler.py -i test.leif -o test.asm)
	$(as test.asm -o test.o)
	$(gcc test.o -o test)


.PHONY: clean
clean:
	rm -f *.asm *.o test
