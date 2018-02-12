build:
	docker build -t awsiot-python .

run:
	docker run -ti \
	--env-file ./envs \
	-w /root \
	-v ${PWD}:/root awsiot-python python index.py
