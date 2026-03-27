.PHONY: install run test clean

install:
	pip install -r requirements.txt

run:
	python src/parser.py

test:
	python -m unittest discover tests

view:
	python src/view.py $(OUTPUT_FILE)   

view-web:
	python src/to_html.py $(OUTPUT_FILE)

clean:
	rm -f anime_top.csv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
