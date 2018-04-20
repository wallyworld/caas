# how to deploy

```bash
export charmBuildDir=###charm build output dir###

charm build ./mysql -o $charmBuildDir/
juju deploy $charmBuildDir/builds/mysql

charm build ./gitlab -o $charmBuildDir/
juju deploy $charmBuildDir/builds/gitlab

```