# Juju CAAS

Charms and layers for Juju deployments on container substrates.

## Building a Charm

Charms use the caas-base layer.
To build a charm during development, set the LAYER_PATH:


`export LAYER_PATH=<this-repo-dir>/layers`

`charm build`
