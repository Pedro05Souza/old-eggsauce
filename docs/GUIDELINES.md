# Code Contribution Guidelines
Contribution to this repository **MUST** follow all of the guidelines below. Adhering to these guidelines ensures code readability and uniformity.


### GitHub
Every new feature **MUST** be created inside a separate branch. New feature branches **MUST** be named in the following pattern: `feat/new-feature-name`.

Any commit's first word **MUST** be a verb in the imperative. Some commit names that follow these guidelines are: *'Add new bot command'*, *'Create new cog for different functionality'*, etc.

Pull Requests **MUST** be reviewed by TWO people before executing any merge. Pull Requests **MUST** pass all automated tests before being sent to a reviewer for approval. A pull request for the branch `feat/new-feature-name` **MUST** follow the following naming pattern `feat: new feature name`.

For more references on commits and pull requests, please refer to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) documentation.

### Language
Everything inside the code and on GitHub **MUST** be in english. That includes all names, commit messages, pull requests and internal documentation. This excludes messages that will be displayed to the user.

### Naming Conventions

For uniformity we'll be using the `PEP 8` naming conventions for python code.

- Python variables and functions **MUST** be named using *snake_case*.
- Classes **MUST** be named using *PascalCase* and class methods should be named using *snake_case*. 
- Constants **MUST** be named using just *UPPERCASE* text, if it's multiple words, they **MUST** be separated by underscores.
- Modules and packages **MUST** be named using *short lowercase* words. Modules **SHOULD** be separated by underscores, packages **SHOULD NOT** be separated by underscores.