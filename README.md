# mltk_algo_automl
splunk ml toolkit cusomter algo of auto classifier and regressor

# quick start

install the customer algo refer to [https://github.com/splunk/mltk-algo-contrib](https://github.com/splunk/mltk-algo-contrib)

start dataplay container
```sh
docker run -p 8001:8000 dataplay3:0.1-dev
```

# SPL samples
run following spl for the auto ml algorithms

classification sample
```sh
| inputlookup iris.csv
| fit AutoClassifier "species" from "sepal_length", "sepal_width" into "automodel1"
```

```sh
| inputlookup iris.csv | apply automodel1
```

regression sample
```sh
| inputlookup iris.csv
| fit AutoRegressor "sepal_length" from "sepal_width" "petal_length" into "automodel2"
```

```sh
| inputlookup server_power.csv | apply automodel2
```

# issues

as the dependency requests rely on urllib3 and there is a known issue of open ssl on mac, you may need copy the python lib to replace the default one used by splunk which is under `<SPLUNK_HOME>/etc/apps/Splunk_SA_Scientific_Python_darwin_x86_64/bin/darwin_x86_64/bin/python`

the search will fail with auto-finalize under free lincese, an enterprise license is requried.



