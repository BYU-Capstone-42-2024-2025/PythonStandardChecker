# PythonStandardAction

_A github action to be used across python projects in the BYU-Capstone-42-2024-2025 organization_

As a lab, certain standards have been generally adopted, but have had a hard time being actually implemented. This action intends to fix that by acting like a linter, enforcing certain styles.

## Enforced Styles

1. Snake case is enforced on all function and variable name.

2. The use of \_\_ or name mangling is disallowed.

3. Docstring argument definitions must not start with a capital letter and must not use a period at the end. To indicate additional information in a sentence like format, use semicolons to separate sections. The first letters of these sections can also not be capitalized.

4. Functions are required to have a docstring.

5. Function arguments must have a type annotation.

6. Function arguments may not use mutable items(list, set, dict) as defaults, as python handles defaults stupidly.

7. Functions must specify a return type.

8. Class names must be in pascal case (ex. ExampleClass)

9. First line of docstring must end with period

10. Classes must have a docstring

11. Function rguments must be documented in a section started with `Args: \n`

12. Docstring argument type must be up to date with the function arguments' type annotations

13. Docstring argument names must be up to date with the function arguments' names

14. When specifying a docstring arguments type, if the argument has a default, the type must be followed with `, optional`

15. Argument defaults must be documented in the `Args: ` section in a section of their corresponding arguments saying `defaults to {default value}`

16. A function's return type must be documented in a section started with `Returns: \n`

17. A function's return type must be exactly equal to the documented type

## Adding action to your workflow

This action is best used in the same section as the meds action. Just add it as another step like the following.

```github
        steps:
            - name: Follow Python Standard
              uses: BYU-Capstone-42-2024-2025/PythonStandardAction@v1.1.0
```

## Excluding files from the check

This action uses a local file `.standardignore` to specify files and other items to not check.

To use this, create a file named `.standardignore` and put in file paths like you would for a `.gitignore` file. The following is an example of entries you could put in your file.

```cmd
**/.*

**/__pycache__
**/img
**/TempFile.py
```

The above entries in a `.standardignore` would have the checker skip over the folders/files that match the pattern, such as private folders, pychache folders, img folders, and the TempFile.py file. The standard checker will already ignore any file not is not a `.py` file, this just allows you to have it ignore general areas and specific ones.

## Excluding variables and functions from the check

Using the `.standardignore` file specified in the section above, specific function and variable names can be skipped over on the check.

The syntax to do so is the use of the `!` before the name of the variable/function to ignore.

For example

```cmd
!sleep_for_retry
```

The above example ignores the sleep_for_retry function when applying standards as the name is required as it is an overwrite of an outside modules functionality.

## Running locally so you don't have to wait on github actions

There isn't a way to do this yet
