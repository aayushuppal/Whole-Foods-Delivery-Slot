setup:
	virtualenv -p python3.7 venv
	./venv/bin/pip install -r requirements.txt

check:
	./venv/bin/pylint wf_ds_chrome.py

run:
	./venv/bin/python3.7 wf_ds_chrome.py

clean:
	rm -rf __pycache__
