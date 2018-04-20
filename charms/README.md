# how to deploy

```bash

charm build ./mysql -o ~/.local/shared/charms/
juju deploy ~/.local/shared/charms/builds/mysql

charm build ./gitlab -o ~/.local/shared/charms/
juju deploy ~/.local/shared/charms/builds/gitlab

```