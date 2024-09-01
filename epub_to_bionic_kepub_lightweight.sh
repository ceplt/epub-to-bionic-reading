#! /bin/bash

# ---- config ----

epub_to_bionic_reading_script_path=""
kepub_to_lightweight_kepub_script_path=""
kepubify_exe_path=""

# ----------------


SAVEIFS=$IFS
IFS=$(echo -en "\n\b")  # to manage files with name containing spaces

for file in $(ls ./); do
    if [[ -f "$file" && "$file" == *.epub && ! "$file" == *___BIONIC* && ! "$file" == *.kepub* ]]; then
        filename_with_bionic=$(echo "$file" | sed -e s/.epub/___BIONIC.epub/g)
        filename_with_converted_kepub_vanilla=$(echo "$filename_with_bionic" | sed -e s/___BIONIC.epub/___BIONIC_converted.kepub.epub/g)
        filename_with_converted_kepub_rework=$(echo "$filename_with_converted_kepub_vanilla" | sed -e s/___BIONIC_converted.kepub.epub/___BIONIC.kepub.epub/g)
        filename_with_converted_kepub_lightweight=$(echo "$filename_with_converted_kepub_rework" | sed -e s/___BIONIC.kepub.epub/___BIONIC___LIGHTWEIGHT.kepub.epub/g)

        if [[ ! (-e "./$file" && -e "./$filename_with_converted_kepub_lightweight") ]]; then
            # --- epub to bionic epub ---
            echo -e "\n-----------------------"
            echo -e "[INFO] processing epub to bionic epub for file: $file"
            python "$epub_to_bionic_reading_script_path" "$file"


            # --- bionic epub to bionic kepub ---
            echo -e "[INFO] processing bionic epub to bionic kepub for file: $filename_with_bionic"
            "$kepubify_exe_path" "$filename_with_bionic"
            mv "$filename_with_converted_kepub_vanilla" "$filename_with_converted_kepub_rework"
            echo -e "[INFO] deleting file: $filename_with_bionic"
            rm -f "$filename_with_bionic"  # we end up with the .epub vanilla file + the *___BIONIC.kepub.epub file


            # --- bionic kepub to lightweight bionic kepub ---
            echo -e "[INFO] processing bionic kepub to lightweight bionic kepub for file: $filename_with_converted_kepub_rework"
            python "$kepub_to_lightweight_kepub_script_path" "$filename_with_converted_kepub_rework"
            echo -e "[INFO] deleting file: $filename_with_converted_kepub_rework"
            rm -f "$filename_with_converted_kepub_rework"  # we end up with the .epub vanilla file + the *___BIONIC___LIGHTWEIGHT.kepub.epub file
            echo -e "-----------------------\n"
        fi
    fi
done

IFS=$SAVEIFS
