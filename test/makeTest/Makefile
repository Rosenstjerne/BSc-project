objects = test quicksort

.PHONY: all
all: $(objects)

%.asm: %.leif
	python ../../src/compiler.py -c 0 -i $^ -o $@ 

%.o: %.asm
	as $^ -o $@

%: %.o
	gcc $^ -o $@


.PHONY: clean
clean:
	rm -f *.asm *.o $(objects)
