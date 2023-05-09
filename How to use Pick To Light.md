# How to use Pick To Light

_based in_  [Part 1 - Send &amp; receive - websockets 10.4 documentation](https://websockets.readthedocs.io/en/stable/intro/tutorial1.html#)

## Prerequisites

if you haven't installed websockets yet, do it now

```
pip install websockets
```

Confirm that websockets is installed

```
python3 -m websockets --version
```

## Step 1.- Setup HTTP server

Open a shell and run this command to start a HTTP server:

```
python3 -m http.server
```

## Step 2.- Boostrap the Server

Run the picker-location server app

```python
python3 app.py
```

## Step 3.- Run/connect the client

goto http://localhost:8000/?location_code=11_ in the browser
