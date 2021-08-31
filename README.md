# WeatherStation
Currently a simple server written in python3 which uses APIs of [https://openweathermap.org/](https://openweathermap.org/).

In order to use application you have to create `apikey` file containing your apikey to [https://openweathermap.org/](https://openweathermap.org/) service in `config` directory.
Server ask API for new forecast/current weather every 10 minutes and shares it in response to messages sent over UDP.

Project also includes Dockerfile, docker-compose.yml and Ansible playbook files to make installation and usage easier.
