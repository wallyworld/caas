# how to deploy

```bash

charm build ./mysql -o ./
# gitlab requires `5.7` mysql
juju deploy ./builds/mysql --config mysql_image=mysql/mysql-server:5.7

charm build ./gitlab -o ./
juju deploy ./builds/gitlab

```