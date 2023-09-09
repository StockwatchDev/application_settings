# Usage in a library package

You can use `application_settings` also to parametrize a library package:

- Define parameters in one or more Section classes (i.e., not in a Container) - best
  practice is to have a single main section with possibly nested sub-sections;
- Use parameters in the code of your library by invoking class method `get()` on your
  Section class(es) (see [chapter on using parameters](./4-Using_parameters.md));
- The application that uses your library has to take care of loading stored values into
  your parameters. This can be done in two ways:
  - If the application also uses `application_settings`, it's simple; the main Section
      of your library package just needs to be contained in the Container of the
      application;
  - If the application does not use `application_settings`, then the application
      should invoke class method `set(data: dict[str, Any])` on your main Section, where
      `data` holds key-value-pairs with the name of the parameter and the value.
      Subsections can be set by the name of the section as key and a nested dictionary
      for the subsection parameters. Note that `set()` should be invoked before any
      `get()` is done.
