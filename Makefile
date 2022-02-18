all:
	./generate
develop:
	find site | entr -c ./generate
