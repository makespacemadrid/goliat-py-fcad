# Modelo en FreeCAD de la impresora/fresadora Goliat realizado con scripts de Python para FreeCAD

El fichero `goliat.py` se ejecuta desde FreeCAD.
Para saber cómo se ejecuta un fichero python en FreeCAD, lee este tutorial:
http://www.freecadweb.org/wiki/index.php?title=Python_scripting_tutorial

Para ejecutar este fichero, ejecuto el FreeCAD en el directorio donde tengo el fichero `goliat.py`

Por ejemplo, en Windows, ejecuto una ventana `cmd`, y voy a mi directorio donde tengo guardados los ficheros de goliat.py. Y desde alli, ejecuto el FreeCAD:

![wincmd](img/cmd_freecad_lauch.jpg)

Y ahora, desde la consola de Python del FreeCAD, ejecuta:

```
execfile('goliat.py')
```

# Dependencias

El fichero `goliat.py` tiene muchas funciones y clases definidas en otros ficheros, agrupados en un repositorio (`comps`)
Estos ficheros estan en https://github.com/felipe-m/fcad-comps

Para mantener un control de versiones y compatibilidad de los ficheros, este repositorio contiene la version de `comps` con que funciona. Estos estan en `modules\comps`. Sin embargo, si por lo que sea, necesitases cambiar comps, yo lo haria desde el repositorio original y me traeria los cambios a Goliat.

De hecho, yo suelo trabajar con los directorios `goliat` y `comps` al mismo nivel. Como `comps` es usado por otros proyectos que estoy haciendo, no tiene sentido tenerlo dentro de goliat.

Un ejemplo de la estructura de ficheros que tengo en mi ordenador seria la siguiente: 
```
cad/
  +-- py_freecad              # python scripts for FreeCAD
      +-- goliat                # goliat scripts
          +-- goliat.py             # Goliat printer
      +-- comps               # library of components
          +-- comps.py            # components
          +-- kcomp.py            # constants about components
          +-- fcfun.py            # library of functions
      +-- corexy              # python scripts for coreXY printer
          +-- carriage.py         # carriage of the 3D printer 
```


