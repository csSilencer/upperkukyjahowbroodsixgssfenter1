# upperkukyjahowbroodsixgssfenter1
suber sigred prozhekt

## Development

### Prerequisites
```
python3
```

### Installation
```
pip install -r requirements.txt
```

### Usage
```
python upperkukyjahowbroodsixgssfenter1/main.py
or
python upperkukyjahowbroodsixgssfenter1/main.py -d True  # debug mode
```


## Release

### Prerequisites
```
docker
```

### Build
```
docker-compose build upperkuk
```

### Run
We bind mount the directory so that the logs output back to the file in our directory
```
docker run -it --mount src="$(pwd)",target=/home/root/upperkuk,type=bind upperkuk
```
