import time
import click
with click.progressbar([1, 2, 3]) as bar:
    for x in bar:
        (f"sleep({x})...")
        time.sleep(x)