#!/bin/bash
echo "Run 'docker stop textx-docs' from another terminal to gracefully terminate." 
docker run -it --rm --name textx-docs -v .:/p -p 3000:3000 igordejanovic/mdbook-textx:latest mdbook serve docs -n 0.0.0.0
