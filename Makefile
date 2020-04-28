all:
	./generate.sh
develop:
	find site | entr -cdp ./generate.sh
