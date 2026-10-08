# Contributing

By submitting a pull request, you agree that your contributions will be licensed under the MIT License as specified in this repository.

## Releases

Releases need no personal tokens or secrets. In GitHub: **Actions → Release → Run workflow** (branch `master`).
The version and the release notes come from the Conventional Commits since the last release (`fix:` → patch,
`feat:` → minor, `feat!:` or `BREAKING CHANGE:` → major); squash-merge pull requests with a conventional title.
The executables are built first; the tag and the release are only created when the build succeeded. To rebuild the
executables of an existing release: **Actions → Publish → Run workflow** with its tag.
