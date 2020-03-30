# Pipe Plot
pipeplot draws a graph in a terminal based on data from pipe. 

## Installation
```bash
pip install pipeplot
```

## Examples of using
### Ping like gping:
```bash
ping ya.ru | grep --line-buffered time | sed -u -e 's#.*time=\([^ ]*\).*#\1#' | pipeplot
```
### Chart of deaths per minute from coronavirus:
```bash
while true; do curl -s https://coronavirus-19-api.herokuapp.com/all | jq '.deaths'; sleep 60; done | pipeplot
```
### Render graphite to console:
```bash
while sleep 5; do curl -s 'http://graphite/render?target=my_app_rps_error&format=json&from=-5min&until=now&maxDataPoints=495' | jq -c '.[0].datapoints[-1]'; done | sed -u s/null/0/ | stdbuf -oL uniq | stdbuf -oL jq '.[0]' | pipeplot
```
