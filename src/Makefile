objects = test quicksort

.PHONY: all
all: $(objects)

%.asm: %.leif
	python compiler.py -c 1 -i $^ -o $@ 

%.o: %.asm
	as $^ -o $@

%: %.o
	gcc $^ -o $@


.PHONY: clean
clean:
	rm -f *.asm *.o $(objects)
