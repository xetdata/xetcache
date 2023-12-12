pandoc -f markdown -t rst README.md > README.rst
python -m build
