@echo off
docker build -t mycelium-docs-mkdocs .
docker run --rm -it -p 8080:8000 -v "%cd%":/docs mycelium-docs-mkdocs
