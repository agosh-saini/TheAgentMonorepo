.PHONY: lint test new-python-app new-next-app new-fullstack-app

lint:
	bash scripts/lint-all.sh

test:
	bash scripts/test-all.sh

new-python-app:
	@[ -n "$(NAME)" ] || (echo "Usage: make new-python-app NAME=myapp" && exit 1)
	bash scripts/create-python-app.sh $(NAME)

new-next-app:
	@[ -n "$(NAME)" ] || (echo "Usage: make new-next-app NAME=myweb" && exit 1)
	bash scripts/create-nextjs-app.sh $(NAME)

new-fullstack-app:
	@[ -n "$(NAME)" ] || (echo "Usage: make new-fullstack-app NAME=myproject" && exit 1)
	bash scripts/create-fullstack-app.sh $(NAME)
