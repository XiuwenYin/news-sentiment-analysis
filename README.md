model需要额外安装pytorch和transformers库
```console
$ pip install transformers
```
```console
$ pip3 install torch torchvision
```
# news-sentiment-analysis

## Dev Env Setup
### Create virtual env
```console
$ python3 -m venv venv
```
### Activate virtual env
```console
$ source venv/bin/activate
```
### Install dependencies
```console
$ pip install -r requirements.txt
```

### Setting the FLASK_APP environment variable
```console
$ export FLASK_APP=news-sentiment-analysis.py
```

### Run the app
```console
$ flask run
```
