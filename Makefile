.PHONY: help test validate strict new clean

help:            ## show this help
	@grep -hE '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

test:            ## run the test suite
	python3 -m unittest discover -s tests -v

validate:        ## validate the examples and any packs, warnings allowed
	python3 scripts/handoff.py validate examples/example-pack.md
	python3 scripts/handoff.py validate examples/example-pack.fa.md
	@set -e; found=0; for p in packs/*-pack.md; do \
	  [ -e "$$p" ] || continue; \
	  found=1; \
	  python3 scripts/handoff.py validate "$$p"; \
	done; \
	[ $$found -eq 0 ] && echo "no packs in packs/ yet" || true

strict:          ## same, but warnings fail too (what CI runs)
	python3 scripts/handoff.py validate examples/example-pack.md --strict
	python3 scripts/handoff.py validate examples/example-pack.fa.md --strict
	@set -e; found=0; for p in packs/*-pack.md; do \
	  [ -e "$$p" ] || continue; \
	  found=1; \
	  python3 scripts/handoff.py validate "$$p" --strict; \
	done; \
	[ $$found -eq 0 ] && echo "no packs in packs/ yet" || true

new:             ## scaffold a pack: make new SLUG=myproject
	@test -n "$(SLUG)" || (echo "usage: make new SLUG=myproject" && exit 1)
	python3 scripts/handoff.py new $(SLUG) --out packs

clean:           ## remove caches
	rm -rf scripts/__pycache__ tests/__pycache__ .pytest_cache
