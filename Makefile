load:
	python src/etl/load_to_sqlite.py

test:
	pytest tests/etl

report:
	python src/etl/manual_review.py

clean:
	del /Q output\*.csv

ratios:
	python src/ratios/ratio_engine.py

dashboard:
	echo Dashboard module pending Sprint 3

api:
	echo API module pending Sprint 4