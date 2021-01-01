run:
	poetry run flask run

migrate:
	poetry run python main.py migrate

test:
	poetry run pytest
