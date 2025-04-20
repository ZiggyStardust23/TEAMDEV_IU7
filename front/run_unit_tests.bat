for %%f in (./tests/*.py) do ( 
    python -B -m unittest tests/%%f
)