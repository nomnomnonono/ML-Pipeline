format:
	poetry run pysen run format
lint:
	poetry run pysen run lint
data:
	cd dataset && poetry run python create_dataset.py
pipeline:
	poetry run python pipeline.py
