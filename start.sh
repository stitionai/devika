docker run -it --rm -v $(pwd).env:/devika/.env -v $(pwd)/config.toml:/devika/config.toml -v $(pwd)/default.conf:/etc/nginx/sites-available/default -p 1337:1337 -p 3001:80 devika-image:latest
