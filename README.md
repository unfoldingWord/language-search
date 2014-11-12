# Auto Completion of Languages

This is a simple Flask app that provides an auto-completion endpoint for a
typeahead module as demonstrated in `example.html`.

![](screenshot.png)


## To Run

* `pip install flask`
* `python autocomplete.py`
* In a separate terminal: `python -m SimpleHTTPServer 8888

Now in a browser you can visit <http://localhost:8888> and type in language
queries and see teh autocomplete work.

For now, it's just saving the selection to a `<div>`.

