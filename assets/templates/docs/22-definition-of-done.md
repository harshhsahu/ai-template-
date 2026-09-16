# 22 Definition of Done

A change is "done" only when all of these are true:

- [ ] Code follows [09-coding-guidelines.md](09-coding-guidelines.md).
- [ ] Server/client boundaries respected; no secrets in the client bundle.
- [ ] Backends fail soft (return `null`, no 500 cascade).
- [ ] Loading / empty / error states handled.
- [ ] Tests added/updated and passing ([19-testing.md](19-testing.md)).
- [ ] Docs updated in the same commit (api / database / modules / infrastructure).
- [ ] No new library added for an already-covered concern.
- [ ] PR is small and single-concern ([23-git-workflow.md](23-git-workflow.md)).
