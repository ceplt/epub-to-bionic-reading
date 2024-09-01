# epub-to-bionic-reading

Fork from https://github.com/GLorentz1/bionic-reading

Scripts to convert an .epub file into the bionic reading version of it, plus special features for the kobo e-reader


## Purpose of the scripts

The purpose of this script is to automate the process of converting EPUB files into the bionic reading format. The ebook styling/formatting might be impacted.


## Use of script epub-to-bionic-reading.py

Run the script using the following command (the default output_file name is `input_file___BIONIC.epub`)

```
python ./epub-to-bionic-reading.py input_file.epub [output_file.epub]
```

## Special features for the kobo e-reader

### Kepub conversion

To set the line spacing and other parameters of an epub correctly on the kobo, you need to convert the files to kepub format using this utility -> `https://github.com/pgaskin/kepubify`

```
./kepubify-windows-64bit.exe book.epub
```

### Kepub lightweight conversion (kepub + bionic reading issue)

The kepub format adds koboSpan tags to ALL bold tags, and an epub converted to bionic reading is full of them. This makes the kobo e-reader lag, so __after converting to kepub__ you'll have to lighten the file by keeping the tags used for navigation in the chaptering, but delete the others that are -imo- useless (things that the kobo uses for stats like reading speed and stuff)

```
python ./kepub_to_lightweight_kepub.py input_file.epub [output_file.epub]
```

## Wrapper for bionic + kepub + lightweight multiple conversions

Script to convert all epub files in a directory to a bionic + kepub + lightweight version, if it doesn't already exist

/!\ to be executed in the directory containing the epub files !

Set scripts and kepubify paths in the `config` part of the script then run it

```
./epub_to_bionic_kepub_lightweight.sh
```
