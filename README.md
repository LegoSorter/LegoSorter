# LegoSorter

## How to run

```
export LEGO_HOME=<set your lego home directory>
bash start.sh

// example of generating images
blender --background --addons importldraw --python render.py -- --width 400 --height 400 --output_dir "output" --part "ldraw/parts/1.dat" --scene "scenes/simple.blend" --ldraw "ldraw" --samples 6
```
