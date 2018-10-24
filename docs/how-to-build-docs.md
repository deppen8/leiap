# Procedure to build `leiap` docs

1. [Build](https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives) and [install](https://packaging.python.org/tutorials/installing-packages/#installing-from-local-archives) the latest version of the package.
2. Navigate to `leiap/docs`
3. If any new modules have been added, they will need to be added to the `modules.rst` file.
4. Run Makefile (`$ make html`). This will put a new version of the docs in a separate folder: `../../leiap-docs/html`. This folder is also connected to the `leiap` repo, but it only contains the docs.
5. Navigate to `../../leiap-docs/html`
6. `git add .`
7. `git commit -m <message>`
8. `git push origin gh-pages` NOTE: the `gh-pages` part is VERY important. This is the branch that the docs webpage is built from. Pushing to `master` does nothing for the docs.
