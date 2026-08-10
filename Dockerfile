FROM squidfunk/mkdocs-material:9.7.6

RUN apk add --no-cache bash

RUN pip install --no-cache-dir \
      mkdocs-git-revision-date-localized-plugin \
      mkdocs-minify-plugin \
      mkdocs-git-authors-plugin \
      mkdocs-title-casing-plugin \
      mkdocs-glightbox \
      markdown-include \
      mkdocs-redirects \
      mkdocs-section-index \
      tzdata
