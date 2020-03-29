## Samples
### Ping:
```bash
ping ya.ru | grep --line-buffered time | sed -u -e 's#.*time=\([^ ]*\).*#\1#' | ./pipeplot.py
```
### Chart of deaths per minute from coronavirus:
```bash
while true; do curl -s https://coronavirus-19-api.herokuapp.com/all | jq '.deaths'; sleep 60; done | ./pipeplot.py
```
