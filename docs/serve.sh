#!/bin/bash
echo "Run 'docker stop textx-docs' from another terminal to gracefully terminate." 
docker run -it --rm --name textx-docs -v .:/docs -p 3000:3000 igordejanovic/mdbook-textx:latest mdbook serve -n 0.0.0.0
